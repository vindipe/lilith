#!/bin/bash


# CONFIG section --------------------------------
set -e
export DEBIAN_FRONTEND=noninteractive


# HELP section ----------------------------------
usage() {
  local exit_code="${1:-1}"

  echo "Usage: $0 [-flag <value>]"
  echo ""
  echo "Options:"
  echo "  -i, --implementation <STR>    Blockchain to use (default: poa)"
  echo "  -r, --ram <INT>               RAM to use (default: 16)"
  echo "  -c, --cores <INT>             vCPU Cores to use (default: 8)"
  echo "  -m, --mode <STR>              Network Shape (default: full-mesh)"
  echo "  -b, --bandwidth <INT>         Bandwidth on blockchain nodes (default: 1)"
  echo "  --size <INT>                  Nodes per region (default: 1)"
  echo "  -s, --secondaries <INT>       Number of Secondaries to use (default: 10)"
  echo "  -l, --link <STR>              Links selection strategy (default: hop)"
  echo "  --dataset <STR>               Network Dataset to use (default: diablo)"
  echo "  --check <INT>                 Latency-check (default: 0)"
  echo "  --dynamic <INT>               Dynamic action (default: 0:none)"
  echo "  --switch <INT>                Number of switches (default: 0:topo_v1)"
  echo "  --latency <INT>               Latency between switches (default: 0:topo_v1)"
  echo "  --validate-only               Validate inputs/configuration and exit before build/deploy"
  exit "$exit_code"
}


# FUNCTIONS section ----------------------------------
terminate_child_processes() {
    if declare -p machines >/dev/null 2>&1; then
        for machine in "${machines[@]}"; do
          (
            ssh -O exit "$machine" >/dev/null 2>&1 || true
          ) &
        done
        wait
    fi

    pkill -P $$ >/dev/null 2>&1 || true
}


trap 'terminate_child_processes' EXIT SIGINT SIGTERM KILL

get_timestamp() {
    date +"%Y-%m-%d %H:%M:%S"
}

ssha() {
  local machine_value="$1"
  local command="$2"

  local strict_host_key_checking="${LILITH_SSH_STRICT_HOST_KEY_CHECKING:-accept-new}"
  local connect_timeout="${LILITH_SSH_CONNECT_TIMEOUT:-30}"

  mkdir -p misc/logs/ssh

  local safe_machine_name
  safe_machine_name="$(printf '%s' "$machine_value" | tr -c 'A-Za-z0-9_.-' '_')"

  local ssh_log_path="misc/logs/ssh/ssh_${safe_machine_name}.log"

  local command_prefix=""
  if [[ "${LILITH_EXECUTION_PROFILE:-remote}" == "local" ]]; then
    command_prefix='export LILITH_SUDO_CMD=""; export LILITH_SKIP_SYSTEMCTL=1; export LILITH_SKIP_HOST_SETUP=1; export LILITH_SKIP_KOLLAPS_DEPLOY=1; export LILITH_DISABLE_DASHBOARD_TRIGGER=1; export DOCKER_CONFIG="$HOME/.docker-lilith-local"; mkdir -p "$DOCKER_CONFIG"; if [ ! -f "$DOCKER_CONFIG/config.json" ]; then printf "{}\n" > "$DOCKER_CONFIG/config.json"; fi; sudo() { if [ "${1:-}" = "-n" ]; then shift; fi; "$@"; }; systemctl() { echo "Skipping systemctl $*" >&2; return 0; }; service() { if [ "${1:-}" = "docker" ]; then echo "Skipping service $*" >&2; return 0; fi; command service "$@"; }; '
  fi

  set +e
  ssh \
    -C \
    -T \
    -o "StrictHostKeyChecking=${strict_host_key_checking}" \
    -o "LogLevel=ERROR" \
    -o "ConnectTimeout=${connect_timeout}" \
    -E "$ssh_log_path" \
    "$machine_value" \
    "${command_prefix}${command}"

  local ssh_exit_code=$?
  set -e

  {
    echo "############################"
    echo "Timestamp: $(get_timestamp)"
    echo "Machine: $machine_value"
    echo "Exit code: $ssh_exit_code"
    echo "Command: $command"
    echo "############################"
    echo ""
    echo ""
  } >> "$ssh_log_path"

  sleep 2

  return "$ssh_exit_code"
}



validate_only_run() {
    echo ""
    echo "#######################################################"
    echo "Validate-only mode ..."
    echo "#######################################################"

    local failed=0
    local implementation_worker="misc/lilith/lilith-${implementation}"
    local dataset_file="misc/${dataset}-aws.csv"
    local ping_file="misc/cloudping/ping.csv"
    local fixes_dir="kollaps/examples/diablo/primary/fixes"
    local tmp_dir="kollaps/examples/diablo/primary/tmp"

    echo "Execution profile: ${LILITH_EXECUTION_PROFILE:-remote}"
    echo "Implementation: ${implementation}"
    echo "Dataset: ${dataset}"
    echo "Topology mode: ${mode}"
    echo "Machines: ${#machines[@]}"

    if [[ ${#machines[@]} -eq 0 ]]; then
        echo "ERROR: no active machines configured."
        failed=1
    else
        printf 'Configured machines:\n'
        printf '  - %s\n' "${machines[@]}"
    fi

    if [[ "${LILITH_EXECUTION_PROFILE:-remote}" == "local" ]]; then
        if [[ ${#machines[@]} -ne 1 || "${machines[0]}" != "localhost" ]]; then
            echo "ERROR: local execution profile expects machines.txt to contain only localhost."
            failed=1
        fi
    fi

    if [[ ! -f "$implementation_worker" ]]; then
        echo "ERROR: missing implementation worker: $implementation_worker"
        failed=1
    else
        echo "OK: implementation worker found: $implementation_worker"
    fi

    if [[ ! -f "$dataset_file" ]]; then
        echo "ERROR: missing dataset file: $dataset_file"
        failed=1
    else
        echo "OK: dataset file found: $dataset_file"
    fi

    if [[ ! -s "$ping_file" ]]; then
        echo "ERROR: missing or empty cloud ping dataset: $ping_file"
        failed=1
    else
        echo "OK: cloud ping dataset found: $ping_file"
    fi

    if [[ ! -d "$fixes_dir" ]]; then
        echo "ERROR: missing fixes directory: $fixes_dir"
        failed=1
    else
        local workload_count
        workload_count=$(find "$fixes_dir" -maxdepth 1 -name 'workload-*.yaml' | wc -l)
        if [[ "$workload_count" -eq 0 ]]; then
            echo "ERROR: no workload YAML files found in $fixes_dir"
            failed=1
        else
            echo "OK: workload YAML files found in fixes: $workload_count"
        fi
    fi

    if [[ ! -d "$tmp_dir" ]]; then
        echo "ERROR: missing primary runtime tmp directory: $tmp_dir"
        failed=1
    else
        echo "OK: primary runtime tmp directory found: $tmp_dir"
    fi

    for generated_file in \
        "$tmp_dir/id_ed25519" \
        "$tmp_dir/aws.csv" \
        "$tmp_dir/run.tmp" \
        "kollaps/examples/diablo/id_ed25519.pub"
    do
        if [[ -e "$generated_file" ]]; then
            echo "WARN: generated runtime file currently exists: $generated_file"
        fi
    done

    if [[ "$failed" -ne 0 ]]; then
        echo "Validate-only failed."
        exit 1
    fi

    echo "Validate-only completed successfully."
}

remote_preflight() {
    echo ""
    echo "#######################################################"
    echo "Remote preflight checks ..."
    echo "#######################################################"

    local failed=0
    local pids=()
    local execution_profile="${LILITH_EXECUTION_PROFILE:-remote}"

    for machine in "${machines[@]}"; do
        (
            echo "Checking ${machine} ..."

            if ! ssha "${machine}" "true" >/dev/null 2>&1; then
                echo "Error: cannot connect to ${machine} through SSH." >&2
                exit 1
            fi

            if [[ "$execution_profile" == "local" ]]; then
                if ! ssha "${machine}" "docker version >/dev/null 2>&1"; then
                    echo "Error: ${machine} cannot run Docker without sudo in local profile." >&2
                    echo "Check Docker Desktop integration or run: docker version" >&2
                    exit 1
                fi
            else
                if ! ssha "${machine}" "sudo -n true" >/dev/null 2>&1; then
                    echo "Error: ${machine} does not allow non-interactive sudo." >&2
                    echo "Configure passwordless sudo for the benchmark user, or prepare the host manually before running Lilith." >&2
                    exit 1
                fi
            fi

            echo "OK: ${machine}"
        ) &
        pids+=("$!")
    done

    for pid in "${pids[@]}"; do
        if ! wait "$pid"; then
            failed=1
        fi
    done

    if [[ "$failed" -ne 0 ]]; then
        echo "Remote preflight failed. Aborting before starting the benchmark." >&2
        exit 1
    fi
}


init() {
    local implementation_value="$1"
    local secondaries_value="$2"
    local network_size_value="$3"
    local mode_value="$4"
    local cores_value="$5"
    local ram_value="$6"
    local bandwidth_value="$7"
    local link_strategy_value="$8"
    local dataset_value="$9"
    local dynamic_value="${10}"
    local switch_value="${11}"
    local latency_value="${12}"

    # Generate the Kollaps topology xml file
    if [ "$switch_value" -eq 0 ]; then
      python3 scripts/gen_topo.py --secondaries "$secondaries_value" --nodes "$network_size_value" --type "$mode_value" --bandwidth "$bandwidth_value" --strategy "$link_strategy_value" --dataset "$dataset_value" --dynamic "$dynamic_value" --blockchain "$implementation_value"
    else
      if [ "$latency_value" -ge 1 ]; then
        python3 scripts/gen_topo_v2.py --secondaries "$secondaries_value" --nodes "$network_size_value" --type "$mode_value" --bandwidth "$bandwidth_value" --strategy "$link_strategy_value" --dataset "$dataset_value" --dynamic "$dynamic_value" --blockchain "$implementation_value" --switch "$switch_value" --latency "$latency_value"
      else
        python3 scripts/gen_topo_v2.py --secondaries "$secondaries_value" --nodes "$network_size_value" --type "$mode_value" --bandwidth "$bandwidth_value" --strategy "$link_strategy_value" --dataset "$dataset_value" --dynamic "$dynamic_value" --blockchain "$implementation_value" --switch "$switch_value"
      fi
    fi

    # Save the complete topology
    cp kollaps/examples/topology.xml misc/logs/topology_complete.xml

    # Select the blockchain-specific Lilith worker.
    lilith_worker_source="misc/lilith/lilith-${implementation_value}"
    lilith_worker_target="kollaps/examples/diablo/primary/fixes/lilith"

    if [[ ! -f "$lilith_worker_source" ]]; then
      echo "Error: missing Lilith worker for implementation: ${implementation_value}" >&2
      echo "Expected file: $lilith_worker_source" >&2
      echo "Available workers:" >&2
      find misc/lilith -maxdepth 1 -type f -name 'lilith-*' -printf '  %f\n' | sort >&2
      exit 1
    fi

    cp "$lilith_worker_source" "$lilith_worker_target"
    chmod +x "$lilith_worker_target"

    # Create the file to get the experiment infos
    echo "${implementation_value}-cores${cores_value}-ram${ram_value}-secondaries${secondaries_value}-bandwidth${bandwidth_value}-dataset:${dataset_value}-size${network_size_value}-strategy:${link_strategy_value}-dynamic:${dynamic_value}-switch:${switch_value}-latency:${latency_value}-${mode_value}" > "misc/logs/${implementation_value}.tmp"
    cp "misc/logs/${implementation_value}.tmp" kollaps/examples/diablo/primary/tmp/run.tmp

    # Save the dataset
    cp "misc/${dataset_value}-aws.csv" kollaps/examples/diablo/primary/tmp/aws.csv

    # Put the Diablo structure inside Kollaps dir
    cp -r kollaps/examples kollaps/Kollaps

    echo ""
    echo "#######################################################"
    echo "Initialization Phase ..."
    echo "#######################################################"
    for machine in "${machines[@]}"; do
        echo "Sync ${machine} ..."
        # due to rsync issue when more machines in the set
        sleep 5
        (
            ssha "${machine}" "export DEBIAN_FRONTEND=noninteractive"

            set +e
            # Kill previous execution on each machine
            # ssha "${machine}" "sudo pkill -f 'build-kollaps.sh'"
            ssha "${machine}" "pgrep -f 'build-kollaps.sh' | while read -r pid; do sudo -n kill \"$pid\" 2>/dev/null || true; done"
            set -e

            rsync -avzh --delete kollaps/Kollaps "${machine}":.
            # rsync -avzh --delete kollaps/kollaps.tar.gz "${machine}":.
            # ssha "${machine}" "tar -xzvf kollaps.tar.gz"
            # ssha "${machine}" "sudo rm -f kollaps.tar.gz"

            # # Put the Diablo structure inside Kollaps dir
            # rsync -avzh kollaps "${machine}":.
            # ssha "${machine}" "mv kollaps/build-kollaps.sh . && chmod +x build-kollaps.sh"
            ssha "${machine}" "mkdir -p ~/lilith-runtime"
        rsync -avzh kollaps/build-kollaps.sh "${machine}:lilith-runtime/build-kollaps.sh"
            ssha "${machine}" "chmod +x ~/lilith-runtime/build-kollaps.sh && test -x ~/lilith-runtime/build-kollaps.sh"

            # set +e
            docker_exist=$(ssha "${machine}" "which docker")
            if [ -n "$docker_exist" ]; then
                echo "Docker is installed on the ${machine} machine." >> misc/logs/kollaps.log
            else
                echo "Docker is not installed on the ${machine} machine. Attempting to install it..." >> misc/logs/kollaps.log
                ssha "${machine}" "~/lilith-runtime/build-kollaps.sh init_docker"
                echo "Docker installation successful." >> misc/logs/kollaps.log

                # ssha "${machine}" "sudo reboot"
                # echo "Rebooting the ${machine} machine. Waiting for 3 minutes..."
                # sleep 180
            fi
            # set -e

            ssha "${machine}" "~/lilith-runtime/build-kollaps.sh init"
        ) & #> /dev/null 2>&1 &
    done
    wait

    echo ""
    echo "#######################################################"
    echo "Swarm creation Phase ..."
    echo "#######################################################"

    echo "Previous Docker stack removal"
    ssha "${machines[0]}" "sudo -n docker stack rm kollaps >/dev/null 2>&1 || true"

    manager="${machines[0]}"

    for machine in "${machines[@]}"; do
        if [ "${machine}" != "$manager" ]; then
            (
                ssha "${machine}" "sudo -n docker swarm leave --force >/dev/null 2>&1 || true"
                ssha "${machine}" "sudo -n systemctl restart docker >/dev/null 2>&1 || true"
                ssha "${machine}" "sudo -n docker network rm kollaps_network >/dev/null 2>&1 || true"
            ) &
        fi
    done
    wait

    echo "Initializing Docker Swarm manager on ${manager} ..."
    ssha "${manager}" "mkdir -p ~/lilith-runtime"
    ssha "${manager}" "sudo -n docker swarm leave --force >/dev/null 2>&1 || true"
    ssha "${manager}" "sudo -n systemctl restart docker >/dev/null 2>&1 || true"

    if [[ "${LILITH_EXECUTION_PROFILE:-remote}" == "local" ]]; then
        ssha "${manager}" "sudo -n docker swarm init --advertise-addr 127.0.0.1 > ~/lilith-runtime/swarm_init_output.txt"
    else
        ssha "${manager}" "sudo -n docker swarm init > ~/lilith-runtime/swarm_init_output.txt"
    fi

    manager_state=$(ssha "${manager}" "sudo -n docker info --format '{{.Swarm.LocalNodeState}} {{.Swarm.ControlAvailable}}'")
    echo "Manager swarm state: ${manager_state}"

    if [[ "$manager_state" != "active true" ]]; then
        echo "Error: ${manager} is not an active Docker Swarm manager." >&2
        echo "Docker reported: ${manager_state}" >&2
        exit 1
    fi

    rsync -avzhr "${manager}:lilith-runtime/swarm_init_output.txt" misc/logs/

    ssha "${manager}" "sudo -n docker network create --driver=overlay --subnet=10.1.0.0/24 kollaps_network >/dev/null 2>&1 || true"

    echo "Docker and Kollaps Build completed"

    join_command=$(grep -o 'docker swarm join --token [^ ]* [^ ]*:[^ ]*' misc/logs/swarm_init_output.txt | tr -d '\n' || true)

    if [[ "${#machines[@]}" -gt 1 && -z "$join_command" ]]; then
        echo "Error: could not extract Docker Swarm join command from misc/logs/swarm_init_output.txt" >&2
        exit 1
    fi

    for machine in "${machines[@]}"; do
        if [ "${machine}" != "$manager" ]; then
            echo "${machine} joining ..."
            (
                ssha "${machine}" "sudo -n ${join_command}"
            ) &
        else
            echo "${machine} as swarm manager..."
        fi
    done
    wait

    echo "Kollaps cluster created"
}

build(){
    local cores_value="$1"
    local ram_value="$2"

    echo ""
    echo "#######################################################"
    echo "Build Phase ..."
    echo "#######################################################"

    ssha "${machines[0]}" "~/lilith-runtime/build-kollaps.sh build ${cores_value} ${ram_value}"

    # Topology fixing section (Kollaps-private repo)
    python3 scripts/xml-fix.py
    cp kollaps/examples/topology.xml misc/logs/topology.xml
    for machine in "${machines[@]}"; do
        # due to rsync issue when more machines in the set
        sleep 3
        (
            rsync -avzh kollaps/examples/topology.xml "${machine}":Kollaps/examples/topology.xml
        ) & #> /dev/null 2>&1 &
    done
    wait

    echo ""
    echo "#######################################################"
    echo "Deploying Phase ..."
    echo "#######################################################"
    ssha "${machines[0]}" "~/lilith-runtime/build-kollaps.sh deploy"

    echo ""
    echo "#######################################################"
    echo "Logs Phase ..."
    echo "#######################################################"
    rsync -avzh "${machines[0]}":~/Kollaps/examples/topology.yaml misc/logs/topology.yaml #> /dev/null 2>&1
    for machine in "${machines[@]}"; do
        (
          # rsync -avzh "${machine}":~/Kollaps/examples/topology.xml "misc/logs/topology-${machine}.xml" #> /dev/null 2>&1
          god_container=$(ssha "${machine}" "sudo -n docker ps --format '{{.Names}}' | grep 'god_' | head -n 1")
          set +o errexit
          if [[ -n $god_container ]]; then
            echo $god_container
            ssha "${machine}" "sudo -n docker logs ${god_container}" > "misc/logs/logs_$god_container.txt"
            ssha "${machine}" "sudo -n docker exec ${god_container} cat logs.txt" > "misc/logs/logs_ti_$god_container.txt"
          fi
          set -o errexit
        ) & #> /dev/null 2>&1 &
    done
    wait
}

bench() {
    # Export the arguments to pass to the Minion script (Kollaps-private repo)
    rsync -avzh "${machines[0]}":~/Kollaps/examples/arguments.txt ./misc/logs
    arguments=$(<misc/logs/arguments.txt)

    echo ""
    echo "#######################################################"
    echo "Bench Phase ..."
    echo "#######################################################"
    ssha "${machines[0]}" "~/lilith-runtime/build-kollaps.sh bench"

    # Manual start of Secondaries (Kollaps-private repo)
    for machine in "${machines[@]}"; do
        (
            secondaries=$(ssha "${machine}" "sudo -n docker ps --format '{{.Names}}' | grep 'kollaps_secondary*'")
            if [ ${#secondaries} -gt 0 ]; then
              for secondary_container in ${secondaries}; do
                # echo "$secondary_container"

                # Start the secondary
                ssha "${machine}" "sudo -n docker exec ${secondary_container} bash /entity.sh"
              done
            fi
        ) & #> /dev/null 2>&1 &
    done
    wait

    for machine in "${machines[@]}"; do
        (
            primary_container=$(ssha "${machine}" "sudo -n docker ps --format '{{.Names}}' | grep 'kollaps_primary*' | head -n 1")
            if [[ -n $primary_container ]]; then
                echo "Primary (${primary_container}) on ${machine}..."
                echo "Primary (${primary_container}) on ${machine}..." >> misc/logs/kollaps.log

                # To get the IP of the services
                ssha "${machine}" "sudo -n docker exec ${primary_container} bash /init-minion.sh ${arguments}"

                # LATENCY-check
                if [[ $check -eq 1 ]]; then
                    echo "CHECK" >> misc/logs/kollaps.log
                    ssha "${machine}" "sudo -n docker exec ${primary_container} bash /tmp/latencies.sh"
                fi
            fi
        ) & #> /dev/null 2>&1 &
    done
    wait

    for machine in "${machines[@]}"; do
        (
            # Start Measurements on the machines
            ssha "${machine}" "~/lilith-runtime/build-kollaps.sh measure ${machine}" > /dev/null 2>&1 &

            primary_container=$(ssha "${machine}" "sudo -n docker ps --format '{{.Names}}' | grep 'kollaps_primary*' | head -n 1")
            if [[ -n $primary_container ]]; then
                # Run the "minion.sh" script inside the container with the commands taken from the variable
                ssha "${machine}" "sudo -n docker exec ${primary_container} bash /minion.sh ${execution}"
            fi
        ) & #> /dev/null 2>&1 &
    done
    wait

    echo "Benchmark completed"
}

export_results() {
    mkdir -p results

    echo ""
    echo "#######################################################"
    echo "Exporting Results Phase ..."
    echo "#######################################################"

    tmp_file=$(find misc/logs -maxdepth 1 -type f -name '*.tmp' -print -quit)
    tmp_content=$(< "$tmp_file")

    # Extract values from the .tmp file content
    IFS='-' read -ra tmp_values <<< "$tmp_content"
    implementation_result="${tmp_values[0]}"
    cores_result="${tmp_values[1]}"
    ram_result="${tmp_values[2]}"
    secondaries_result="${tmp_values[3]}"
    bandwidth_result="${tmp_values[4]}"
    dataset_result="${tmp_values[5]}"
    network_size_result="${tmp_values[6]}"
    link_strategy_result="${tmp_values[7]}"
    dynamic_result="${tmp_values[8]}"
    switch_result="${tmp_values[9]}"
    latency_result="${tmp_values[10]}"
    mode_result=""
    for (( i=11; i<${#tmp_values[@]}; i++ )); do
      mode_result+="${tmp_values[i]}-"
    done

    folder_name="${implementation_result}-${cores_result}-${ram_result}-${secondaries_result}-${bandwidth_result}-${dataset_result}-${network_size_result}-${link_strategy_result}-${dynamic_result}-${switch_result}-${latency_result}-${mode_result}$(date +"%Y-%m-%d_%H-%M-%S")"
    # echo $folder_name

    path_to_results="results"

    if [ "$dynamic" -ne 0 ]; then
        if [ "$dynamic" -eq 1 ]; then
            path_to_results="results/dynamic/packet-drop"
        elif [ "$dynamic" -eq 2 ]; then
            path_to_results="results/dynamic/bw-congestion"
        elif [ "$dynamic" -eq 3 ]; then
            path_to_results="results/dynamic/switch-leave"
        elif [ "$dynamic" -eq 4 ]; then
            path_to_results="results/dynamic/node-crash"
        elif [ "$dynamic" -eq 5 ]; then
            path_to_results="results/dynamic/lat-evo"
        fi
    fi
    if [ "$switch" -ne 0 ]; then
        path_to_results="results/new"
    fi

    mkdir -p "$path_to_results/$folder_name"

    folder_export="$path_to_results/$folder_name"


    for machine in "${machines[@]}"; do
      (
        # rm log files
        ssha "${machine}" "find ./results/ -type f \( -name 'err' -o -name 'out' -o -name '*_err*' -o -name 'results.json' \) -exec rm {} +"

        ssha "${machine}" "~/lilith-runtime/build-kollaps.sh results > /dev/null"

        rsync -avzh "${machine}":results/* $folder_export
        for file in $folder_export/*.tar.gz; do
            (
              tar -xzvf "$file" -C $folder_export
              rm -f -- "$file"
            ) &
        done
        wait
      ) > /dev/null 2>&1 &
    done
    wait

    total_size=$(du -s $folder_export | awk '{print $1}')
    total_size_mb=$((total_size / 1024))

    echo "Export completed: ${total_size_mb} MB"

    # PLOTs
    mkdir -p $folder_export/img

    set +e
    python3 scripts/quantiles.py $folder_export
    python3 scripts/plots_json.py $folder_export
    python3 scripts/energy_consume.py $folder_export
    # python3 scripts/plots.py $folder_export

    df_path=$(find "$folder_export" -type f -name "kollaps-df.csv" -exec dirname {} \;)
    echo $df_path
    if [ -n "$df_path" ]; then
      python3 scripts/kollaps_df_plotting.py "${#machines[@]}" "$df_path" "$bandwidth_result" "$dataset_result"
    fi
    set -e

    mkdir -p $folder_export/kollaps_logs
    cp -r misc/logs/* $folder_export/kollaps_logs

    # find $folder_export/ -type f \( -name 'err' -o -name '*tar.gz*' -o -name 'out' -o -name '*_err*' -o -name 'results.json' \) -exec rm {} +
    find $folder_export/ -type f \( -name 'err' -o -name '*tar.gz*' -o -name 'out' -o -name '*_err*' \) -exec rm {} +
}

reset(){
    echo ""
    echo "#######################################################"
    echo "Reset ..."
    echo "#######################################################"

    echo "Removing local Kollaps clone..."
    rm -rf -- kollaps/Kollaps

    local remote_cleanup_command='
set -e

echo "Removing previous Docker stack if present..."
sudo -n docker stack rm kollaps >/dev/null 2>&1 || true
sleep 60

echo "Removing Docker images if present..."
sudo -n docker images -q | while read -r image_id; do sudo -n docker rmi "$image_id" >/dev/null 2>&1 || true; done

echo "Pruning Docker system..."
sudo -n docker system prune -af >/dev/null 2>&1 || true

echo "Removing Lilith-generated files from remote home..."
sudo -n rm -rf -- "$HOME/Kollaps" "$HOME/build-kollaps.sh" "$HOME/swarm_init_output.txt" "$HOME/results" "$HOME/energy"
'

    for machine in "${machines[@]}"; do
        echo "Reset ${machine} environment ..."
        (
            ssha "${machine}" "$remote_cleanup_command"
        ) &
    done

    wait
}



# DEFAULT VALUES section ----------------------------------
implementation="poa"
cores=8
ram=16
secondaries=10
network_size=1
mode="full-mesh"
bandwidth=1
link_strategy="hop"
dataset="diablo"
check=0
dynamic=0
switch=0
latency=0

logfile="misc/logs/timing.txt"
validate_only=0

for arg in "$@"; do
  case "$arg" in
    -h|--help)
      usage 0
      ;;
  esac
done

machines_file="machines.txt"
machines=()

if [[ ! -f "$machines_file" ]]; then
    echo "Error: missing $machines_file." >&2
    echo "Create it from machines.example.txt and add one SSH target per non-comment line." >&2
    exit 1
fi

while IFS= read -r line || [[ -n "$line" ]]; do
    # Trim leading and trailing whitespace.
    line="${line#"${line%%[![:space:]]*}"}"
    line="${line%"${line##*[![:space:]]}"}"

    # Ignore empty lines and comments.
    [[ -z "$line" || "$line" == \#* ]] && continue

    machines+=("$line")

    set +e
    ssh -O exit "$line" >/dev/null 2>&1 || true
    set -e
done < "$machines_file"

if [[ ${#machines[@]} -eq 0 ]]; then
    echo "Error: $machines_file does not contain any active SSH target." >&2
    echo "Add one machine per line, for example: user@node-1.example.com" >&2
    exit 1
fi

# ARGS section ----------------------------------
while [[ $# -gt 0 ]]; do
  case "$1" in
    --switch)
      switch="$2"
      if ! [[ "$switch" =~ ^[0-9]+$ ]]; then
        echo "Error: the switch value is not an integer: $switch"
        exit 1
      fi
      shift 2
      ;;
    --latency)
      latency="$2"
      if ! [[ "$latency" =~ ^[0-9]+$ ]]; then
        echo "Error: the latency value is not an integer: $latency"
        exit 1
      elif [[ "$switch" -eq 0 && "$latency" -ge 1 ]]; then
        echo "Error: The switch value must be greater than 0 to use the latency parameter"
        exit 1
      elif [[ "$switch" -ge 1 && "$latency" -eq 0 ]]; then
        echo "Error: The latency value must be greater than 0"
        exit 1
      fi
      shift 2
      ;;
-b|--bandwidth)
      bandwidth="$2"
      if [[ "$switch" -eq 0 ]]; then
        if ! [[ "$bandwidth" -ge 1 && "$bandwidth" -le 10 ]]; then
          echo "Error: The bandwidth value must be between 1 and 10: $bandwidth"
          exit 1
        fi
      else
        if ! [[ $(bc <<< "$bandwidth >= 0.001 && $bandwidth <= 10") -eq 1 ]]; then
          echo "Error: The bandwidth value must be between 0.001 and 10: $bandwidth"
          exit 1
        fi
      fi
      shift 2
      ;;
    -i|--implementation)
      implementation="$2"
      valid_implementations=("algorand" "poa" "quorum" "diem" "solana")
      if [[ ! " ${valid_implementations[@]} " =~ " ${implementation} " ]]; then
          echo "Error: The implementation value must be either 'algorand', 'poa', 'quorum', 'diem' or 'solana'. You have insert: $implementation"
          exit 1
      fi
      shift 2
      ;;
    -r|--ram)
      ram="$2"
      if ! [[ "$ram" =~ ^[0-9]+$ ]]; then
        echo "Error: The value of 'ram' is not an integer: $ram"
        exit 1
      fi
      shift 2
      ;;
    -c|--cores)
      cores="$2"
      if ! [[ "$cores" =~ ^[0-9]+$ ]]; then
        echo "Errore: Il valore di cores non è un intero: $cores"
        exit 1
      fi
      shift 2
      ;;
    -s|--secondaries)
      secondaries="$2"
      if ! [[ "$secondaries" =~ ^[0-9]+$ ]]; then
        echo "Error: The value of 'secondaries' is not an integer: $secondaries"
        exit 1
      fi
      shift 2
      ;;
    -m|--mode)
      mode="$2"
      if [[ ! "$mode" =~ ^(full-mesh|scale-free-t|scale-free-l|scale-free-r|double-l|double-s|torus-l|torus-t|torus-r|fat-tree-t|fat-tree-l|hypercube)$ ]]; then
        echo "Error: The value of mode must be 'full-mesh', 'scale-free-t', 'scale-free-l', 'scale-free-r', 'double-l', 'double-s', 'torus-l', 'torus-t', 'torus-r', 'fat-tree-t', 'fat-tree-l', or 'hypercube', but it is: $mode"
        exit 1
      fi
      shift 2
      ;;
    -l|--link)
      link_strategy="$2"
      if [[ ! "$link_strategy" =~ ^(latency|hop)$ ]]; then
        echo "Error: The value of link selection strategy must be either 'latency' or 'hop', but it is: $link_strategy"
        exit 1
      fi
      shift 2
      ;;
    --dataset)
      dataset="$2"
      if [[ ! "$dataset" =~ ^(our|diablo)$ ]]; then
        echo "Error: The value of dataset must be either 'our' or 'diablo', but it is: $dataset"
        exit 1
      fi
      shift 2
      ;;
    --size)
      network_size="$2"
      if ! [[ "$network_size" =~ ^[0-9]+$ ]] || ((network_size < 1)); then
        echo "Error: The network size value is not an integer or not greater than 1: $network_size"
        exit 1
      fi
      shift 2
      ;;
    --check)
      check="$2"
      if ! [[ "$check" =~ ^[01]$ ]]; then
        echo "Error: The latency check value must be either 0 or 1: $check"
        exit 1
      fi
      shift 2
      ;;
    --dynamic)
      dynamic="$2"
      if ! [[ "$dynamic" =~ ^[012345]$ ]]; then
        echo "Error: The dynamic value must be either 0, 1, 2, 3, 4, or 5: $dynamic"
        exit 1
      fi
      shift 2
      ;;
    -h|--help)
      usage 0
      ;;
    "results")
      export_results
      exit 0
      ;;
    "reset")
      set +o errexit
      reset
      exit 0
      ;;
    --validate-only)
      validate_only=1
      shift
      ;;
    *)
      echo "Error: Unknown argument $1"
      usage 1
      ;;
  esac
done

if [ "$mode" = "hypercube" ] && [ "$switch" -ne 0 ]; then
  echo "Error: hypercube topology is only supported by the topology v1 generator." >&2
  echo "Use --switch 0, or choose another mode supported by topology v2." >&2
  exit 1
fi

if [ "$dynamic" -eq 5 ] && [ "$switch" -ne 0 ]; then
  echo "Error: dynamic=5 latency evolution is only supported by the topology v1 generator." >&2
  echo "Use --switch 0, or choose a dynamic mode between 0 and 4 for topology v2." >&2
  exit 1
fi

if [ "$switch" -eq 0 ] && [ "$dynamic" -eq 0 ]; then
  execution=0
elif [ "$switch" -eq 0 ] && [ "$dynamic" -ne 0 ]; then
  execution=2
elif [ "$switch" -ne 0 ]; then
  execution=1
fi

echo ""
echo "#######################################################"
echo "Clean Previous sessions ..."
echo "#######################################################"
pids=$(ps aux | grep -E "run\.sh" | grep -vE "multi-run\.sh|grep|$$" | awk '{print $2}')

if [ -n "$pids" ]; then
    echo "Processes found: "
    # Remove the process in case it still runs
    for pid in $pids; do
        if ps -p $pid > /dev/null; then
            echo "Killing process $pid"
            kill $pid > /dev/null 2>&1 || true
        else
            echo "Process $pid not found"
        fi
    done
else
    echo "Nothing found to be removed"
fi



# ------------------------ MAIN section ----------------------------------

if [[ "$validate_only" -eq 1 ]]; then
    validate_only_run
    exit 0
fi

# DEPENDENCIES section ----------------------------------
echo ""
echo "#######################################################"
echo "Preparing runtime dependencies ..."
echo "#######################################################"
./scripts/requirements.sh --runtime-only

if [[ ! -d "kollaps/Kollaps" ]]; then
    echo "Error: missing kollaps/Kollaps." >&2
    echo "Run ./scripts/requirements.sh once before launching experiments." >&2
    exit 1
fi

# Local logs cleanup section ----------------------------------
mkdir -p misc/logs
rm -f -- misc/logs/*.*
rm -rf -- misc/logs/ssh
mkdir -p misc/logs/ssh

# time measurements
echo "Time.log" > "$logfile"
echo "" >> "$logfile"

# start
remote_preflight

start_time=$(get_timestamp)
init "$implementation" "$secondaries" "$network_size" "$mode" "$cores" "$ram" "$bandwidth" "$link_strategy" "$dataset" "$dynamic" "$switch" "$latency"
end_time=$(get_timestamp)
execution_time=$(($(date -d "$end_time" +%s) - $(date -d "$start_time" +%s)))
echo "Execution time of the INIT process: $execution_time seconds"
echo "Execution time of the INIT process: $execution_time seconds" >> "$logfile"

start_time=$(get_timestamp)
build "$cores" "$ram"
end_time=$(get_timestamp)
execution_time=$(($(date -d "$end_time" +%s) - $(date -d "$start_time" +%s)))
echo "Execution time of the BUILD process: $execution_time seconds"
echo "Execution time of the BUILD process: $execution_time seconds" >> "$logfile"

start_time=$(get_timestamp)
bench
end_time=$(get_timestamp)
execution_time=$(($(date -d "$end_time" +%s) - $(date -d "$start_time" +%s)))
echo "Execution time of the BENCH process: $execution_time seconds"
echo "Execution time of the BENCH process: $execution_time seconds" >> "$logfile"

start_time=$(get_timestamp)
export_results
end_time=$(get_timestamp)
execution_time=$(($(date -d "$end_time" +%s) - $(date -d "$start_time" +%s)))
echo "Execution time of the RESULTS process: $execution_time seconds"
echo "Execution time of the RESULTS process: $execution_time seconds" >> "$logfile"