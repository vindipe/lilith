#!/bin/bash


set -o errexit
# set +o errexit

export DEBIAN_FRONTEND=noninteractive


ssha() {
  local machine_value=$1
  local command=$2

  ssh -o LogLevel=ERROR -o ControlMaster=auto -o ControlPersist=60 -o ControlPath=/tmp/lilith-diablo-%r@%h:%p "$machine_value" "$command" #> /dev/null 2>&1
      # -o UserKnownHostsFile=/dev/null 

  sleep 2
}

if [ $# -eq 0 ]; then
    echo "You need to pass the execution value to the minion script."
    exit 1
fi

if ! [[ "$1" =~ ^[012]$ ]]; then
    echo "The minion execution value must be either 0, 1, or 2"
    exit 1
fi

echo $1

while IFS= read -r line || [ -n "$line" ]; do
    extracted=$(echo "$line" | grep -oE 'root@[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+')
    machines+=("$extracted")
done < setup.txt

# Diablo's fixes section
git clone -b aec https://github.com/lebdron/minion
cp /fixes/setup.txt minion
cp /fixes/install-* minion/script/remote/linux/apt
cp /fixes/solana minion/script/remote
cp /fixes/poa minion/script/remote
cp /fixes/quorum-ibft minion/script/remote
cp /fixes/diablo-worker minion/script/remote
cp /fixes/lilith minion/bin
chmod +x minion/bin/lilith
cp /fixes/*.yaml minion

# Some legacy workload definitions are currently staged in /tmp and copied
# into the primary container by the Dockerfile.
cp /tmp/workload-dota.yaml minion

runs=10

if [ "$1" -eq 0 ]; then
    workloads=("gafam-long" "paypal" "visa" "10000" "football" "dota")
elif [ "$1" -eq 1 ]; then    
    workloads=("football")
elif [ "$1" -eq 2 ]; then    
    workloads=("paypal")
    # workloads=("paypal-long")
    # workloads=("gafam-long")
    runs=1
fi

# sentinel to use to skip the installation and deploy each time
sentinel=0

for workload in "${workloads[@]}"; do
    for ((run=1; run<=$runs; run++)); do
        cd minion

        workload_file="workload-$workload.yaml"

        if [[ ! -f "$workload_file" ]]; then
            echo "Error: workload file not found: $workload_file" >&2
            echo "Available workload files:" >&2
            ls -1 workload-*.yaml >&2 || true
            exit 1
        fi

        if [ $sentinel == 0 ]; then

            set +o errexit
            ./bin/lilith "$workload_file" ../setup.txt
            set -o errexit

            sentinel=1
        else
            ./bin/lilith --skip-install "$workload_file" ../setup.txt
        fi

        cd /        

        for machine in "${machines[@]}"; do
            (   
                ssha "${machine}" "mkdir -p '/results/workloads/$workload/$run'"
            ) &
        done        
        wait        

        ./tmp/export.sh "$workload/$run"         
        
        echo "Process completed for workload $workload, run $run"
        sleep 10
    done
done

# create the bench-results of the workloads execution
python3 /tmp/out.py /results

# comment to maintain the logs about primary 
find /results/workloads/ -type f \( -name 'err' -o -name 'out' \) -exec rm {} +