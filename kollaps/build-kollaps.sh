#!/bin/bash


# CONFIG section --------------------------------
set -o errexit
# set +o errexit
export DEBIAN_FRONTEND=noninteractive
HOME_EXPERIMENT=$(pwd)


# FUNCTIONS section ----------------------------------
init_docker() {  
    cd
    sudo apt-get update -yy && sudo apt-get upgrade -yy
    sudo apt-get install -yy w3m apt-transport-https ca-certificates curl software-properties-common

    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
    sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"      

    # sudo install -m 0755 -d /etc/apt/keyrings
    # sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
    # sudo chmod a+r /etc/apt/keyrings/docker.asc        
    # echo \
    #   "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
    #   $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
    #   sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    sudo apt-get update -yy      
    sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -yy

    set +o errexit
    sudo groupadd docker
    sudo usermod -aG docker $USER
    sudo gpasswd -a $USER docker
    sudo systemctl enable docker.service
    sudo systemctl enable containerd.service

    # sudo chown "$USER":"$USER" /home/"$USER"/.docker -R
    # sudo chmod g+rwx "$HOME/.docker" -R

    newgrp docker
    sudo service docker restart
    set -o errexit        

    docker --version
}

init() {  
  sudo apt-get install python3 python3-pip -y
  sleep 3
  pip3 install pandas 
  sudo pip3 install oyaml lxml

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
  sudo docker build -f dockerfiles/Kollaps -t kollaps:2.0 .
  sleep 4
  sudo docker build -f dockerfiles/DeploymentGenerator -t kollaps-deployment-generator:2.0 .
  sleep 4  

  cd "$HOME_EXPERIMENT"/Kollaps/examples  
  rm -f topology.yaml

  # Diablo initialization
  sudo docker build -f diablo/Dockerfile -t entity-image diablo/
  
  sudo docker build -f utils/dashboard/Dockerfile -t kollaps/dashboard:1.0 utils/dashboard/ &
  sudo docker build -f diablo/entity/Dockerfile -t kollaps/entity:1.0 diablo/entity/ &
  sudo docker build -f diablo/primary/Dockerfile -t kollaps/primary:1.0 diablo/primary/
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
  sudo python3 diablo/compose-fix.py "$cores_value" "$ram_value" 
  sleep 3
}

deploy_stack() {  
  echo "Deploying Diablo-benchmark suite ..."
  cd "$HOME_EXPERIMENT"/Kollaps/examples  
  
  sudo docker stack deploy -c topology.yaml kollaps
  
  # Wait time to build the stack
  sleep 60
}

measurements() {
  local node_label="$1"

  rm -rf -- energy
  mkdir -p energy 

  echo "Timestamp,Container ID,Container Name,CPU%,MEM-USAGE/LIMIT,MEM-PERCENTAGE,NET I/O,BLOCK I/O,PIDS" > "energy/docker_stats_output_${node_label}.csv"  

  set +o errexit
  sudo apt-get install linux-tools-common linux-tools-$(uname -r) linux-tools-generic linux-cloud-tools-generic jq -y
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
      
      sudo perf stat -a -e "$events_string" -o perf_output.tmp sleep 5
      # sudo perf stat -a -e power/energy-cores/,power/energy-pkg/,power/energy-ram/ -o perf_output.tmp sleep 5
      energy_cores=$(awk '/energy-cores/ {print $1; found=1; exit} END {if (!found) print 0+0}' perf_output.tmp)
      energy_pkg=$(awk '/energy-pkg/ {print $1; found=1; exit} END {if (!found) print 0+0}' perf_output.tmp)
      energy_ram=$(awk '/energy-ram/ {print $1; found=1; exit} END {if (!found) print 0+0}' perf_output.tmp)

      for dir in /sys/class/powercap/intel-rapl/intel-rapl:*; do
          energy=$(sudo sh -c "cat $dir/energy_uj")
          rapl=$((rapl + energy))
      done
      echo "\"$timestamp\",$energy_cores,$energy_pkg,$energy_ram,$rapl" >> "energy/energy_output_${node_label}.csv"

      sudo rm perf_output.tmp

      sudo docker stats --no-stream --format "table \"$timestamp\",{{.ID}},{{.Name}},{{.CPUPerc}},{{.MemUsage}},{{.MemPerc}},{{.NetIO}},{{.BlockIO}},{{.PIDs}}" | tail -n +2 >> "energy/docker_stats_output_${node_label}.csv"

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
  w3m http://127.0.0.1:8088/
  sleep 2
  w3m http://127.0.0.1:8088/start
  echo "Experiment started"
  sleep 10
}

export_results() {
  container_regex="kollaps_.*"
  
  container_names=$(sudo docker ps --format '{{.Names}}' --filter "name=$container_regex")

  if [ -n "$container_names" ]; then
    for container_name in $container_names; do      
      # To export the secondaries, use the second option
      if [[ "$container_name" != *"bootstrapp"* && "$container_name" != *"dashboard"* && "$container_name" != *"secondary"* ]]; then            
      # if [[ "$container_name" != *"bootstrapp"* && "$container_name" != *"dashboard"* ]]; then
        (
          mkdir -p "$HOME_EXPERIMENT/results/$container_name"
          sudo docker cp "$container_name:/results/." "$HOME_EXPERIMENT/results/$container_name"
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
    sudo rm -rf -- "$HOME_EXPERIMENT/results"
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