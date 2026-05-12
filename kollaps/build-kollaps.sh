#!/bin/bash


# CONFIG section --------------------------------
set -o errexit
# set +o errexit
export DEBIAN_FRONTEND=noninteractive
HOME_EXPERIMENT=$(pwd)

sudo() {
  if [[ "${1:-}" == "-n" ]]; then
    shift
  fi

  if [[ -v LILITH_SUDO_CMD && -z "$LILITH_SUDO_CMD" ]]; then
    "$@"
  else
    command sudo -n "$@"
  fi
}

systemctl() {
  if [[ "${LILITH_SKIP_SYSTEMCTL:-0}" == "1" ]]; then
    echo "Skipping systemctl $*" >&2
    return 0
  fi

  command systemctl "$@"
}

service() {
  if [[ "${LILITH_SKIP_SYSTEMCTL:-0}" == "1" && "${1:-}" == "docker" ]]; then
    echo "Skipping service $*" >&2
    return 0
  fi

  command service "$@"
}


# FUNCTIONS section ----------------------------------
init_docker() {
    cd
    sudo -n apt-get update -yy && sudo -n apt-get upgrade -yy
    sudo -n apt-get install -yy apt-transport-https ca-certificates curl software-properties-common

    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo -n apt-key add -
    sudo -n add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

    # sudo install -m 0755 -d /etc/apt/keyrings
    # sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
    # sudo chmod a+r /etc/apt/keyrings/docker.asc
    # echo \
    #   "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
    #   $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
    #   sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    sudo -n apt-get update -yy
    sudo -n apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -yy

    set +o errexit
    sudo -n groupadd docker
    sudo -n usermod -aG docker $USER
    sudo -n gpasswd -a $USER docker
    sudo -n systemctl enable docker.service
    sudo -n systemctl enable containerd.service


    newgrp docker
    sudo -n service docker restart
    set -o errexit

    docker --version
}

init() {
  if [[ "${LILITH_SKIP_HOST_SETUP:-0}" == "1" ]]; then
    echo "Skipping host Python dependency setup."
  else
    sudo -n apt-get install -y python3 python3-pandas python3-yaml python3-lxml
    sleep 3
  fi

  # Kollaps setup
  cd $HOME_EXPERIMENT

  # # Clone locally Kollaps
  # if [ ! -d "Kollaps" ]; then

  #     # set +o errexit
  #     # set -o errexit

  #     git clone --branch master --depth 1 --recurse-submodules https://github.com/miguelammatos/Kollaps.git
  # fi
  # echo "Kollaps is cloned."

  # # Put the Diablo structure inside Kollaps dir
  # cp -r kollaps/examples Kollaps

  cd Kollaps/
  export DOCKER_BUILDKIT=1
  sudo -n docker build -f dockerfiles/Kollaps -t kollaps:2.0 .
  sleep 4
  sudo -n docker build -f dockerfiles/DeploymentGenerator -t kollaps-deployment-generator:2.0 .
  sleep 4

  cd "$HOME_EXPERIMENT"/Kollaps/examples
  rm -f topology.yaml

  # Diablo initialization
  sudo -n docker build -f diablo/Dockerfile -t entity-image diablo/

  sudo -n docker build -f utils/dashboard/Dockerfile -t kollaps/dashboard:1.0 utils/dashboard/ &
  sudo -n docker build -f diablo/entity/Dockerfile -t kollaps/entity:1.0 diablo/entity/ &
  sudo -n docker build -f diablo/primary/Dockerfile -t kollaps/primary:1.0 diablo/primary/
  wait
}

build() {
  local cores_value="$1"
  local ram_value="$2"

  echo "Building Diablo-benchmark suite ..."
  cd "$HOME_EXPERIMENT"/Kollaps/examples

  # XML to YAML
  ./KollapsDeploymentGenerator ./topology.xml -s topology.yaml

  # sudo chmod 777 topology.yaml

  # Resource constraint
  sudo -n python3 diablo/compose-fix.py "$cores_value" "$ram_value"
  sleep 3
}

deploy_stack() {
  echo "Deploying Diablo-benchmark suite ..."
  cd "$HOME_EXPERIMENT"/Kollaps/examples

  if [[ "${LILITH_SKIP_KOLLAPS_DEPLOY:-0}" == "1" ]]; then
    echo "Skipping Docker stack deploy because LILITH_SKIP_KOLLAPS_DEPLOY=1."
    echo "Local smoke test reached the safe stop point after build/generation."
    return 0
  fi

  sudo -n docker stack deploy -c topology.yaml kollaps

  # Wait time to build the stack
  sleep 60
}

measurements() {
  local node_label="$1"

  rm -rf -- energy
  mkdir -p energy

  echo "Timestamp,Container ID,Container Name,CPU%,MEM-USAGE/LIMIT,MEM-PERCENTAGE,NET I/O,BLOCK I/O,PIDS" > "energy/docker_stats_output_${node_label}.csv"

  set +o errexit
  sudo -n apt-get install linux-tools-common linux-tools-$(uname -r) linux-tools-generic linux-cloud-tools-generic jq -y
  events_string=$(perf list | grep power/energy | awk '{print $1}' | tr '\n' ',' | sed 's/,$//')
  echo "Timestamp,power/energy-cores,power/energy-pkg,power/energy-ram,intel-rapl" > "energy/energy_output_${node_label}.csv"

  # # Get container IDs with "kollaps" in their names
  # container_ids=()
  # container_names=$(docker ps --format "{{.Names}}")

  # # Loop attraverso ogni nome del container
  # for name in $container_names; do
  #     # Controlla se il nome del container contiene "kollaps" ma non "primary", "secondary", "bootstrapper" o "dashboard"
  #     if [[ $name == *"kollaps"* && $name != *"primary"* && $name != *"secondary"* && $name != *"bootstrapper"* && $name != *"dashboard"* ]]; then
  #         # Ottieni l'ID del container e aggiungilo all'array
  #         id=$(docker ps -qf "name=$name")
  #         container_ids+=("$id")
  #         echo "Timestamp,Container Name,CPU%,RAM,RAM%,NET-I-ETH0,NET-O-ETH0,NET-I-ETH1,NET-O-ETH1" > "energy/docker_api_output_${id}_${node_label}.csv"
  #     fi
  # done

  # Stampa gli ID dei container che soddisfano i criteri
  # echo "Container IDs:"
  # for id in "${container_ids[@]}"; do
  #     echo "$id"
  # done

  rapl=0
  while true; do
      timestamp=$(date "+%Y-%m-%d %H:%M:%S")

      sudo -n perf stat -a -e "$events_string" -o perf_output.tmp sleep 5
      # sudo perf stat -a -e power/energy-cores/,power/energy-pkg/,power/energy-ram/ -o perf_output.tmp sleep 5
      energy_cores=$(awk '/energy-cores/ {print $1; found=1; exit} END {if (!found) print 0+0}' perf_output.tmp)
      energy_pkg=$(awk '/energy-pkg/ {print $1; found=1; exit} END {if (!found) print 0+0}' perf_output.tmp)
      energy_ram=$(awk '/energy-ram/ {print $1; found=1; exit} END {if (!found) print 0+0}' perf_output.tmp)

      for dir in /sys/class/powercap/intel-rapl/intel-rapl:*; do
          energy=$(sudo -n sh -c "cat $dir/energy_uj")
          rapl=$((rapl + energy))
      done
      echo "\"$timestamp\",$energy_cores,$energy_pkg,$energy_ram,$rapl" >> "energy/energy_output_${node_label}.csv"

      sudo -n rm perf_output.tmp

      sudo -n docker stats --no-stream --format "table \"$timestamp\",{{.ID}},{{.Name}},{{.CPUPerc}},{{.MemUsage}},{{.MemPerc}},{{.NetIO}},{{.BlockIO}},{{.PIDs}}" | tail -n +2 >> "energy/docker_stats_output_${node_label}.csv"

      # for id in $container_ids; do
      #     prev_cpu_total_usage=$(curl -s --unix-socket /var/run/docker.sock -H 'Content-Type: application/json' http://localhost/containers/$id/stats?stream=false | grep "^{" | jq '.cpu_stats.cpu_usage.total_usage')
      #     prev_cpu_system_total_usage=$(curl -s --unix-socket /var/run/docker.sock -H 'Content-Type: application/json' http://localhost/containers/$id/stats?stream=false | grep "^{" | jq '.cpu_stats.system_cpu_usage')
      #     # echo "CPU total usage for container $id: $prev_cpu_total_usage"
      #     # echo "CPU system total usage for container $id: $prev_cpu_system_total_usage"

      #     (
      #     # CPU stats
      #     cpu_total_usage=$(curl -s --unix-socket /var/run/docker.sock -H 'Content-Type: application/json' http://localhost/containers/$id/stats?stream=false | grep "^{" | jq '.cpu_stats.cpu_usage.total_usage')
      #     echo "CPU total usage for container $id: $cpu_total_usage"

      #     cpu_system_total_usage=$(curl -s --unix-socket /var/run/docker.sock -H 'Content-Type: application/json' http://localhost/containers/$id/stats?stream=false | grep "^{" | jq '.cpu_stats.system_cpu_usage')
      #     echo "CPU system total usage for container $id: $cpu_system_total_usage"

      #     cpu_delta=$(expr $cpu_total_usage - $prev_cpu_total_usage)
      #     echo "CPU delta for container $id: $cpu_delta"

      #     cpu_system_delta=$(expr $cpu_system_total_usage - $prev_cpu_system_total_usage)
      #     echo "CPU system delta for container $id: $cpu_system_delta"

      #     # percentage=$(expr $(expr $cpu_delta - $cpu_system_delta) \* 100)
      #     # percentage_per_cpu=$(echo "$percentage / $n_cpu" | bc)
      #     # echo "Percentage per cpu for container $id: $percentage_per_cpu"
      #     percentage_per_cpu=$(echo "scale=2; ($cpu_delta / $cpu_system_delta) * $n_cpu * 100.0" | bc)
      #     echo "Percentage for container $id: $percentage_per_cpu"

      #     prev_cpu_total_usage=$cpu_total_usage
      #     prev_cpu_system_total_usage=$cpu_system_total_usage

      #     # RAM stats
      #     ram_usage=$(curl -s --unix-socket /var/run/docker.sock -H 'Content-Type: application/json' http://localhost/containers/$id/stats?stream=false | grep "^{" | jq '.memory_stats.usage')
      #     echo "RAM usage for container $id: $ram_usage"

      #     ram_limit=$(curl -s --unix-socket /var/run/docker.sock -H 'Content-Type: application/json' http://localhost/containers/$id/stats?stream=false | grep "^{" | jq '.memory_stats.limit')
      #     echo "RAM limit for container $id: $ram_limit"

      #     percentage_ram=$(expr $(expr $ram_usage / $ram_limit) \* 100)
      #     echo "Percentage RAM for container $id: $percentage_ram"

      #     # Network stats
      #     net_rx_eth0=$(curl -s --unix-socket /var/run/docker.sock -H 'Content-Type: application/json' http://localhost/containers/$id/stats?stream=false | grep "^{" | jq '.networks.eth0.rx_bytes' | awk '{printf "%.2f", $1/1024/1024}')
      #     echo "Network RX bytes for eth0 in container $id: $net_rx_eth0 MB"

      #     net_tx_eth0=$(curl -s --unix-socket /var/run/docker.sock -H 'Content-Type: application/json' http://localhost/containers/$id/stats?stream=false | grep "^{" | jq '.networks.eth0.tx_bytes' | awk '{printf "%.2f", $1/1024/1024}')
      #     echo "Network TX bytes for eth0 in container $id: $net_tx_eth0 MB"

      #     net_rx_eth1=$(curl -s --unix-socket /var/run/docker.sock -H 'Content-Type: application/json' http://localhost/containers/$id/stats?stream=false | grep "^{" | jq '.networks.eth1.rx_bytes' | awk '{printf "%.2f", $1/1024/1024}')
      #     echo "Network RX bytes for eth1 in container $id: $net_rx_eth1 MB"

      #     net_tx_eth1=$(curl -s --unix-socket /var/run/docker.sock -H 'Content-Type: application/json' http://localhost/containers/$id/stats?stream=false | grep "^{" | jq '.networks.eth1.tx_bytes' | awk '{printf "%.2f", $1/1024/1024}')
      #     echo "Network TX bytes for eth1 in container $id: $net_tx_eth1 MB"

      #     name=$(docker inspect --format='{{.Name}}' $id)
      #     echo "Container name for ID $id: $name"

      #     echo "\"$timestamp\",$name,$percentage_per_cpu,$ram_usage,$percentage_ram,$net_rx_eth0,$net_tx_eth0,$net_rx_eth1,$net_tx_eth1" >> "energy/docker_api_output_${id}_${node_label}.csv"
      #     ) #&
      # done
      # wait
  done &
  set -o errexit
}

bench() {
  echo "Running Experiment(s)..."

  if [[ "${LILITH_DISABLE_DASHBOARD_TRIGGER:-0}" == "1" ]]; then
    echo "Skipping dashboard trigger because LILITH_DISABLE_DASHBOARD_TRIGGER=1."
    return 0
  fi

  if ! command -v curl >/dev/null 2>&1; then
    echo "Error: curl is required to trigger the Kollaps dashboard API." >&2
    return 127
  fi

  curl -fsS http://127.0.0.1:8088/ >/dev/null
  sleep 2
  curl -fsS http://127.0.0.1:8088/start >/dev/null

  echo "Experiment started"
  sleep 10
}

export_results() {
  container_regex="kollaps_.*"

  container_names=$(sudo -n docker ps --format '{{.Names}}' --filter "name=$container_regex")

  if [ -n "$container_names" ]; then
    for container_name in $container_names; do
      # To export the secondaries, use the second option
      if [[ "$container_name" != *"bootstrapp"* && "$container_name" != *"dashboard"* && "$container_name" != *"secondary"* ]]; then
      # if [[ "$container_name" != *"bootstrapp"* && "$container_name" != *"dashboard"* ]]; then
        (
          mkdir -p "$HOME_EXPERIMENT/results/$container_name"
          sudo -n docker cp "$container_name:/results/." "$HOME_EXPERIMENT/results/$container_name"
          cd "$HOME_EXPERIMENT/results"
          tar -czvf "$container_name.tar.gz" "$container_name"
          rm -rf -- "$HOME_EXPERIMENT/results/$container_name"
          cd $HOME_EXPERIMENT
        ) &
      fi
    done
    wait
  fi
}


# DEFAULT VALUES section ----------------------------------
case "$1" in
  "init_docker")
    init_docker #> /dev/null 2>&1
    ;;
  "init")
    sudo -n rm -rf -- "$HOME_EXPERIMENT/results"
    mkdir -p "$HOME_EXPERIMENT/results"

    init #> /dev/null 2>&1
    ;;
  "build")
    cores="$2"
    ram="$3"

    build "$cores" "$ram" #"$@" #> /dev/null 2>&1
    ;;
  "measure")
    machine="$2"

    measurements "$machine" #> /dev/null 2>&1 &
    ;;
  "bench")
    bench #> /dev/null 2>&1
    ;;
  "deploy")
    mkdir -p "$HOME_EXPERIMENT/results"
    find "$HOME_EXPERIMENT/results" -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +

    deploy_stack #> /dev/null 2>&1
    ;;
  "results")
    cp -r energy results/

    export_results #> /dev/null 2>&1
    ;;
  *)
    echo "Invalid argument. Usage: $0 { init_docker | init | build | bench | deploy | measure | results }"
    ;;
esac