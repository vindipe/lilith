#!/bin/bash

ssha() {
  local machine_value=$1
  local command=$2
  # local output_file="logs/ssh/ssh_${machine_value}.log"

  ssh -o LogLevel=ERROR -o ControlMaster=auto -o ControlPersist=60 -o ControlPath=/tmp/lilith-diablo-%r@%h:%p "$machine_value" "$command" #> /dev/null 2>&1
      # -o UserKnownHostsFile=/dev/null 

  sleep 2
}

while IFS= read -r line || [ -n "$line" ]; do
    pre_extracted=$(echo "$line" | grep "chain")
    extracted=$(echo "$pre_extracted" | grep -oE 'root@[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+')
    if [ -n "$extracted" ]; then
        machines+=("$extracted")
    fi
done < /setup.txt

for machine in "${machines[@]}"; do
    (   
        # ssh "${machine}" "sudo pkill -f '/resources-measure.sh'"    
        # sleep 2    
        ssha "${machine}" "/resources-measure.sh"
    ) &
done

sleep 3
rm -f /tmp/lilith-diablo-*