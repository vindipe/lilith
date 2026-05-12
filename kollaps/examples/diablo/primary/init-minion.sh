#!/bin/bash


set -o errexit
# set +o errexit

ssha() {
  local machine_value=$1
  local command=$2

  ssh -o LogLevel=ERROR -o ControlMaster=auto -o ControlPersist=60 -o ControlPath=/tmp/lilith-diablo-%r@%h:%p "$machine_value" "$command" #> /dev/null 2>&1
      # -o UserKnownHostsFile=/dev/null 

  sleep 2
}

export DEBIAN_FRONTEND=noninteractive

service ssh start

# Wati for ssh start
while ! nc -z localhost 22; do   
  sleep 1 
done

setup_file="setup.txt"

# Current IP
current_ip=$(hostname -I | awk '{print $1}')
echo "root@$current_ip = primary" > "$setup_file"

# IP by ARGS
for arg in "$@"; do
    service="$arg-$KOLLAPS_UUID"
    service_ip=$(host $service | awk '/has address/ {print $4}')

    case "$arg" in
        *secondary*)
            entry="root@$service_ip = secondary"
            ;;
        *)
            entry="root@$service_ip = chain"
            ;;
    esac

    echo "$entry" >> "$setup_file"    
done    

# save the ip file
cat "$setup_file"
