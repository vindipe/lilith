#!/usr/bin/env bash

set -Eeuo pipefail
IFS=$'\n\t'

usage() {
  cat <<'USAGE'
Usage:
  ./smart-handler.sh --handler <ssh-target> [options]

Description:
  Synchronize the Lilith repository to a remote handler machine and start
  the benchmark workflow in a detached tmux session.

Required:
  -H, --handler <HOST>       SSH target used as the handler machine.
                             It can be a Host alias configured in your SSH client,
                             user@host, or user@ip.

Options:
  -d, --remote-dir <DIR>     Remote directory where Lilith is synchronized.
                             Default: lilith

  -s, --session <NAME>       tmux session name.
                             Default: benchmark_session

  -c, --command <COMMAND>    Command executed inside the tmux session.
                             Default: ./multi-run.sh

      --install-deps         Install minimal handler dependencies using apt:
                             tmux, rsync, openssh-client.
                             Requires sudo on the handler.

  -h, --help                 Show this help message.

Examples:
  ./smart-handler.sh --handler user@handler.example.com

  ./smart-handler.sh \
    --handler my-handler \
    --remote-dir lilith \
    --session lilith_benchmark \
    --command './multi-run.sh'

Notes:
  This script intentionally does NOT copy local SSH credentials and does NOT modify
  the handler system SSH daemon configuration. The handler must already be reachable via SSH.
USAGE
}

handler="${LILITH_HANDLER:-}"
remote_dir="${LILITH_REMOTE_DIR:-lilith}"
session_name="${LILITH_SESSION:-benchmark_session}"
remote_command="${LILITH_COMMAND:-./multi-run.sh}"
install_deps=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    -H|--handler)
      handler="${2:-}"
      shift 2
      ;;
    -d|--remote-dir)
      remote_dir="${2:-}"
      shift 2
      ;;
    -s|--session)
      session_name="${2:-}"
      shift 2
      ;;
    -c|--command)
      remote_command="${2:-}"
      shift 2
      ;;
    --install-deps)
      install_deps=1
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

if [[ -z "$handler" ]]; then
  echo "Error: missing handler." >&2
  echo "Pass it with --handler <ssh-target> or set LILITH_HANDLER." >&2
  exit 1
fi

if [[ -z "$remote_dir" ]]; then
  echo "Error: remote directory cannot be empty." >&2
  exit 1
fi

if [[ -z "$session_name" ]]; then
  echo "Error: tmux session name cannot be empty." >&2
  exit 1
fi

if [[ -z "$remote_command" ]]; then
  echo "Error: remote command cannot be empty." >&2
  exit 1
fi

required_local_items=(
  "kollaps"
  "misc"
  "scripts"
  "run.sh"
  "multi-run.sh"
  "machines.txt"
)

for item in "${required_local_items[@]}"; do
  if [[ ! -e "$item" ]]; then
    echo "Error: required local item not found: $item" >&2
    if [[ "$item" == "machines.txt" ]]; then
      echo "Create it from machines.example.txt and fill it with your cluster SSH targets." >&2
    fi
    exit 1
  fi
done

if ! command -v rsync >/dev/null 2>&1; then
  echo "Error: rsync is not installed locally." >&2
  exit 1
fi

if ! command -v ssh >/dev/null 2>&1; then
  echo "Error: ssh is not installed locally." >&2
  exit 1
fi

mkdir -p misc/logs/ssh

safe_handler_name="$(printf '%s' "$handler" | tr -c 'A-Za-z0-9_.-' '_')"
ssh_log_path="misc/logs/ssh/ssh_${safe_handler_name}.log"

remote() {
  local command="$1"

  ssh \
    -C \
    -T \
    -o LogLevel=ERROR \
    -E "$ssh_log_path" \
    "$handler" \
    "$command"
}

echo "Checking SSH connectivity to handler: $handler"
remote "echo 'Connected to handler: '\"\$(hostname)\""

if [[ "$install_deps" -eq 1 ]]; then
  echo "Installing minimal dependencies on handler..."
  remote "sudo apt-get update -y && sudo apt-get install -y tmux rsync openssh-client"
fi

echo "Checking handler dependencies..."
remote "command -v tmux >/dev/null 2>&1 || { echo 'Error: tmux is not installed on the handler. Re-run with --install-deps or install tmux manually.' >&2; exit 1; }"
remote "command -v rsync >/dev/null 2>&1 || { echo 'Error: rsync is not installed on the handler. Re-run with --install-deps or install rsync manually.' >&2; exit 1; }"

echo "Creating remote directory: $remote_dir"
remote "mkdir -p '$remote_dir'"

echo "Synchronizing Lilith repository to handler..."
rsync -avzh --delete \
  --exclude='.git/' \
  --exclude='.vscode/' \
  --exclude='.idea/' \
  --exclude='venv/' \
  --exclude='.venv/' \
  --exclude='results/' \
  --exclude='temp/' \
  --exclude='misc/logs/' \
  --exclude='tmux-session.log' \
  --exclude='struttura.txt' \
  --exclude='machines.local.backup' \
  --exclude='*.pem' \
  --exclude='*.key' \
  --exclude='id_ed25519' \
  --exclude='id_ed25519.pub' \
  ./ "$handler:$remote_dir/"

echo "Starting tmux session: $session_name"
remote "cd '$remote_dir' && tmux kill-session -t '$session_name' >/dev/null 2>&1 || true"
remote "cd '$remote_dir' && tmux new-session -d -s '$session_name'"
remote "tmux pipe-pane -t '$session_name' -o 'exec cat > $remote_dir/tmux-session.log'"
remote "tmux send-keys -t '$session_name' 'cd $remote_dir && $remote_command' Enter"

echo "Lilith workflow started on handler."
echo ""
echo "Attach to the remote session with:"
echo "  ssh -t $handler 'tmux attach -t $session_name'"
echo ""
echo "Remote log:"
echo "  $remote_dir/tmux-session.log"
