#!/bin/bash


ssha() {
  local machine_value=$1
  local command=$2
  # local output_file="logs/ssh/ssh_${machine_value}.log"

  ssh -o LogLevel=ERROR -o ControlMaster=auto -o ControlPersist=60 -o ControlPath=/tmp/lilith-diablo-%r@%h:%p "$machine_value" "$command" #> /dev/null 2>&1
      # -o UserKnownHostsFile=/dev/null 

  sleep 2
}

# Check arg
if [ $# -ne 1 ]; then
    echo "Usage: $0 <workload/run>"
    exit 1
fi

workload="$1"

# Safety guard: workload is expected to be a relative path such as
# "paypal-long/1" or "gafam-long/1".
if [[ -z "$workload" ]]; then
    echo "Error: workload path cannot be empty." >&2
    exit 1
fi

if [[ "$workload" = /* ]]; then
    echo "Error: workload path must be relative: $workload" >&2
    exit 1
fi

if [[ "$workload" == *".."* ]]; then
    echo "Error: workload path must not contain '..': $workload" >&2
    exit 1
fi

if [[ "$workload" == *"//"* ]]; then
    echo "Error: workload path must not contain empty path components: $workload" >&2
    exit 1
fi

if [[ ! "$workload" =~ ^[A-Za-z0-9._/-]+$ ]]; then
    echo "Error: workload path contains unsupported characters: $workload" >&2
    exit 1
fi


while IFS= read -r line || [ -n "$line" ]; do
    extracted=$(echo "$line" | grep -oE 'root@[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+')
    machines+=("$extracted")
done < /setup.txt

for machine in "${machines[@]}"; do
    # echo $machine
    ssha "${machine}" "sudo pkill -f '/resources-measure.sh'"    
    # sleep 2    
    if [ "${machine}" != "${machines[0]}" ]; then
        (   
            ssha "${machine}" "sudo find /results/workloads/$workload -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +"             
            ssha "${machine}" "sudo rm -rf -- /results/latencies"             

            # ssha "${machine}" "sudo cp -r ~/deploy/* /results"
            # ssha "${machine}" "find ~/deploy -type f \( -name 'err' -o -name 'out' \) -exec cp {} /results/workloads/$workload \;"
            # ssha "${machine}" "find ~/deploy -type f \( -name 'err' -o -name 'out' \) -exec bash -c 'for file; do cp "$file" "/results/workloads/$workload/$(basename "$(dirname "$file")")_$(basename "$file")"; done' bash {} +"
            ssha "${machine}" 'find ~/deploy -type f \( -name "err" -o -name "out" \) -exec bash -c '\''for file; do cp "$file" "/results/workloads/'"${workload}"'/$(basename "$(dirname "$file")")_$(basename "$file")"; done'\'' bash {} +'
            # ssha "${machine}" "sudo find /results/ -type f -name '*agreement.cdv' -exec rm -f {} +"            

            # ssha "${machine}" "find ~/deploy -type f -name 'err' -exec cp {} /results/workloads/$workload \;"
            # ssha "${machine}" "ls /tmp/measurements/"
            # ssha "${machine}" "vnstat > /tmp/measurements/vnstat_output.txt"
            # ssha "${machine}" "ls /tmp/measurements/"
            # sleep 2
            ssha "${machine}" "cp -r /tmp/measurements/* /results/workloads/$workload"
            # ssha "${machine}" "ls /tmp/measurements/"
            ssha "${machine}" "sudo find /tmp/measurements -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +"        
            # ssha "${machine}" "ls /tmp/measurements/"
            # ssha "${machine}" "mv /minion/*.tar.gz /results/"
        ) > /dev/null 2>&1 &
    else
        (                 
            # ssha "${machine}" "sudo cp -r ~/deploy/* /results"
            # ssha "${machine}" "sudo find /results/ -type f -name '*agreement.cdv' -exec rm -f {} +"

            ssha "${machine}" "find ~/deploy -type f \( -name 'err' -o -name 'out' \) -exec cp {} /results/workloads/$workload \;"
            # ssha "${machine}" "find ~/deploy -type f -name 'out' -exec cp {} /results/workloads/$workload \;"
            ssha "${machine}" "cp ~/deploy/diablo/workload.yaml /results/workloads/$workload/../"
            # ssha "${machine}" "vnstat > /tmp/measurements/vnstat_output.txt"
            # sleep 2
            ssha "${machine}" "cp -r /tmp/measurements/* /results/workloads/$workload"
            ssha "${machine}" "sudo find /tmp/measurements -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +"      

            # ssha "${machine}" "mv /minion/*.tar.gz /results/workloads/$workload"
            # ssha "${machine}" "mv /minion/*.results /results/workloads/$workload"
        ) > /dev/null 2>&1 &   
    fi
done
wait

# cp -r ~/deploy/* /results
gzip -d -c ~/deploy/diablo/primary/results.json.gz > results/workloads/$workload/results.json

rm -f /tmp/lilith-diablo-*
rm -rf -- /results/latencies
