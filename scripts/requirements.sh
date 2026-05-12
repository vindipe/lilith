#!/usr/bin/env bash

set -Eeuo pipefail
IFS=$'\n\t'

usage() {
  cat <<'USAGE'
Usage:
  ./scripts/requirements.sh [options]

Description:
  Install local Lilith dependencies, clone Kollaps when needed, generate
  the container SSH key pair when missing, and create runtime directories.

Options:
  --with-ssh-server       Also install openssh-server on this machine.
                          Disabled by default.

  --tune-sshd             Append Lilith-specific SSH daemon limits to
                          /etc/ssh/sshd_config and restart SSH.
                          Requires --with-ssh-server and sudo.
                          Disabled by default.

  --skip-kollaps-clone    Do not clone the upstream Kollaps repository.

  --skip-keygen           Do not generate the container SSH key pair.

  -h, --help              Show this help message.

Examples:
  ./scripts/requirements.sh

  ./scripts/requirements.sh --with-ssh-server --tune-sshd
USAGE
}

with_ssh_server=0
tune_sshd=0
skip_kollaps_clone=0
skip_keygen=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --with-ssh-server)
      with_ssh_server=1
      shift
      ;;
    --tune-sshd)
      tune_sshd=1
      shift
      ;;
    --skip-kollaps-clone)
      skip_kollaps_clone=1
      shift
      ;;
    --skip-keygen)
      skip_keygen=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 1
      ;;
  esac
done

if [[ "$tune_sshd" -eq 1 && "$with_ssh_server" -ne 1 ]]; then
  echo "Error: --tune-sshd requires --with-ssh-server." >&2
  exit 1
fi

echo "Installing local system dependencies..."
sudo apt-get update -y

base_packages=(
  python3
  python3-pip
  rsync
  git
  openssh-client
)

if [[ "$with_ssh_server" -eq 1 ]]; then
  base_packages+=(openssh-server)
fi

sudo apt-get install -y "${base_packages[@]}"

echo "Installing Python dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install \
  pandas \
  matplotlib \
  numpy \
  networkx \
  lxml \
  seaborn \
  scipy

if [[ "$with_ssh_server" -eq 1 && "$tune_sshd" -eq 1 ]]; then
  echo "Applying optional SSH daemon tuning..."

  if ! grep -qF "# Lilith SSH tuning" /etc/ssh/sshd_config; then
    sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.lilith.bkp

    sudo tee -a /etc/ssh/sshd_config >/dev/null <<'SSHD'
# Lilith SSH tuning
MaxAuthTries 20
MaxSessions 50
MaxStartups 100
ClientAliveCountMax 200
ClientAliveInterval 100
SSHD

    echo "Restarting SSH service..."
    sudo service ssh restart
  else
    echo "Lilith SSH daemon tuning already present."
  fi
fi

if [[ "$skip_kollaps_clone" -ne 1 ]]; then
  echo "Checking Kollaps source tree..."

  mkdir -p kollaps

  if [[ ! -d "kollaps/Kollaps" ]]; then
    git clone \
      --branch master \
      --depth 1 \
      --recurse-submodules \
      https://github.com/miguelammatos/Kollaps.git \
      kollaps/Kollaps
  else
    echo "Kollaps is already cloned."
  fi
fi

if [[ "$skip_keygen" -ne 1 ]]; then
  echo "Checking container SSH key pair..."

  public_key="kollaps/examples/diablo/id_ed25519.pub"
  private_key="kollaps/examples/diablo/primary/tmp/id_ed25519"

  mkdir -p kollaps/examples/diablo/primary/tmp

  if [[ ! -e "$public_key" && ! -e "$private_key" ]]; then
    ssh-keygen -t ed25519 -f kollaps/examples/diablo/id_ed25519 -N '' -q
    mv kollaps/examples/diablo/id_ed25519 "$private_key"
    chmod 600 "$private_key"
    chmod 600 "$public_key"
    echo "Container SSH key pair generated."
  else
    echo "Container SSH key pair already exists."
  fi
fi

echo "Creating runtime directories..."
mkdir -p results
mkdir -p results/img
mkdir -p results/plot/performance
mkdir -p results/plot/network
mkdir -p results/plot/energy
mkdir -p misc/logs/ssh

echo "Dependencies setup completed."
