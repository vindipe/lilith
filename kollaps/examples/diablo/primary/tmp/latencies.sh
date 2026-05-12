#!/bin/bash


set -o errexit

ssha() {
  local strict_host_key_checking="${LILITH_SSH_STRICT_HOST_KEY_CHECKING:-accept-new}"

  ssh \
    -o "StrictHostKeyChecking=${strict_host_key_checking}" \
    -o "LogLevel=ERROR" \
    "$@"
}


get_timestamp() {
    date +"%Y-%m-%d %H:%M:%S"
}

test(){
    # for machine in "${machines[@]}" ; do        
    # done
    # wait

    # eval $(ssh-agent) > /dev/null

    for from in "${machines[@]}" ; do        
        from_hostname=$(ssha root@${from} 'cat /etc/hostname')
        if [[ $from_hostname == *"secondary"* || $from_hostname == "primary" || $from_hostname =~ -n([2-9])$ ]]; then
            continue
        fi
        # Remove "-n1" at the end of the string (1 node per region)
        from_hostname=$(echo "$from_hostname" | sed 's/-n1$//')
        echo "IP: $from"
        echo "From-Hostname: $from_hostname"
        for to in "${machines[@]}"; do
            to_hostname=$(ssha root@${to} 'cat /etc/hostname')
            if [ "${to}" = "${from}" ] || [[ $to_hostname == *'secondary'* || $to_hostname == *'primary'* || $to_hostname =~ -n([2-9])$ ]]; then
                continue
            fi            
            to_hostname=$(echo "$to_hostname" | sed 's/-n1$//')            
            echo "IP: $to"
            echo "To-Hostname: $to_hostname"

            # IPERF3 (server)
            # ssha "root@${to}" "iperf3 -s -1 -p 5000 --json > /results/latencies/iperf3-server-${from_hostname}-to-${to_hostname}.json" &
            ssha "root@${to}" "iperf3 -s -1 -p 5000 --logfile '/results/latencies/iperf3-server-${from_hostname}-to-${to_hostname}.log'" &
            sleep 4

            # IPERF3 (client)
            ssha "root@${from}" "iperf3 -c ${to} --get-server-output -t 10 -p 5000 --json > /results/latencies/iperf3-client-${from_hostname}-to-${to_hostname}.json"
            wait
        done

        sleep 3

        # CONTROLLO PER RIMUOVERE
        # ssha "root@${to}" "cat /results/iperf3-server-${from_hostname}-to-${to_hostname}.json" > /results/latencies/iperf3-server-${from_hostname}-to-${to_hostname}.json

        # scp -r "root@${to}:/results/latencies/iperf3-server*" /results/latencies/ > /dev/null &
        # scp -r "root@${from}:/results/latencies/iperf3-client*" /results/latencies/ > /dev/null &

        # echo ""
        # echo "Waiting....."
        # wait

        echo "Next -> "
        echo ""
    done

    echo ""
    echo "Waiting....."
    wait

    for machine in "${machines[@]}" ; do 
      scp -r "root@${machine}:/results/latencies/*" ./results/latencies/ > /dev/null &
    done
    wait

    echo "Completed"
}

sanitize(){
    # rm -f /results/kollaps-df.csv

    # I incorporate the ability to resolve hostnames and then integrate
    # hostname translation into the Python script to obtain a graph similar
    # to that of diablo-aws.csv.

    python3 /tmp/kollaps-p2p-latencies.py
    rm -rf -- /results/latencies
}


while IFS= read -r line || [ -n "$line" ]; do    
    extracted=$(echo "$line" | awk -F'@| ' '$4 == "chain" {print $2}')        
    if [ -n "$extracted" ]; then
        machines+=("$extracted")        
    fi
done < /setup.txt

case "$1" in
  "test")
    test
    ;;
  "sanitize")
    sanitize
    ;;    
  "help")
    echo "Invalid argument. Usage: $0 {test|sanitize}"
    exit 1
    ;;
  *)
    start_time=$(get_timestamp)
    test
    end_time=$(get_timestamp)
    execution_time=$(($(date -d "$end_time" +%s) - $(date -d "$start_time" +%s)))
    echo "Execution time of the TEST LATENCIES process : $execution_time seconds"

    # In case we have more than 1 node per region
    if [ ${#machines[@]} -le 10 ]; then
      sanitize
    fi
    ;;    
esac