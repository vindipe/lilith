#!/bin/bash


# Convert vnstat GiB in MiB
convert_to_mib() {
  local value=$1
  local unit=$2

  case $unit in
      KiB) echo "$value / 1024" | bc ;;
      MiB) echo "$value" | bc ;;
      GiB) echo "$value * 1024" | bc ;;
      *) echo "0" | bc ;;
  esac

#   echo "$value"
}

# service vnstat start

mkdir -p /tmp/measurements

output_file="/tmp/measurements/resources_stats.csv"

network_interface_eth0="eth0"
network_interface_eth1="eth1"

if [ ! -e "$output_file" ]; then
    echo "Timestamp,CPU Usage(%),RAM Usage(MB),vnstat-eth0-Rx(MiB-s),vnstat-eth0-Tx(MiB-s),vnstat-eth1-Rx(MiB-s),vnstat-eth1-Tx(MiB-s)" > "$output_file"
# else
#     # Salva in una variabile l'ultimo numero nel nome del file
#     last_version_resources=$(echo "$output_file" | grep -oP '(?<=resources_stats_)\d+(?=.csv)')
#     # Incremento di uno e salvo il nuovo nome del file
#     last_version_resources=$((last_version_resources + 1))
#     output_file="/tmp/measurements/resources_stats_${last_version_resources}.csv"
fi

# vnstat_eth0_rx=$(vnstat | awk '/^ eth0/ {getline; print $2}')
# echo "vnstat | awk eth0 getline; print 2 : ${vnstat_eth0_rx}"
# sleep 10
# unit_eth0_rx=$(vnstat | awk '/^ eth0/ {getline; print $3}')
# echo "vnstat | awk eth0 getline; print 3 : ${unit_eth0_rx}"
# sleep 10
# vnstat_eth0_rx_pre=$(convert_to_mib "$vnstat_eth0_rx" "$unit_eth0_rx")
# echo "convert_to_mib vnstat_eth0_rx unit_eth0_rx : ${vnstat_eth0_rx_pre}"
# sleep 10

# vnstat_eth0_tx=$(vnstat | awk '/^ eth0/ {getline; print $5}')
# echo "vnstat | awk eth0 getline; print 2 : ${vnstat_eth0_tx}"
# sleep 10
# unit_eth0_tx=$(vnstat | awk '/^ eth0/ {getline; print $6}')
# echo "vnstat | awk eth0 getline; print 3 : ${unit_eth0_tx}"
# sleep 10
# vnstat_eth0_tx_pre=$(convert_to_mib "$vnstat_eth0_tx" "$unit_eth0_tx")
# echo "convert_to_mib vnstat_eth0_tx unit_eth0_tx : ${vnstat_eth0_tx_pre}"
# sleep 10

# vnstat_eth1_rx=$(vnstat | awk '/^ eth1/ {getline; print $2}')
# echo "vnstat | awk eth0 getline; print 2 : ${vnstat_eth1_rx}"
# sleep 10
# unit_eth1_rx=$(vnstat | awk '/^ eth1/ {getline; print $3}')
# echo "vnstat | awk eth0 getline; print 3 : ${unit_eth1_rx}"
# sleep 10
# vnstat_eth1_rx_pre=$(convert_to_mib "$vnstat_eth1_rx" "$unit_eth1_rx")
# echo "convert_to_mib vnstat_eth0_rx unit_eth0_rx : ${vnstat_eth1_rx_pre}"
# sleep 10

# vnstat_eth1_tx=$(vnstat | awk '/^ eth1/ {getline; print $5}')
# echo "vnstat | awk eth0 getline; print 2 : ${vnstat_eth1_tx}"
# sleep 10
# unit_eth1_tx=$(vnstat | awk '/^ eth1/ {getline; print $6}')
# echo "vnstat | awk eth0 getline; print 3 : ${unit_eth1_tx}"
# sleep 10
# vnstat_eth1_tx_pre=$(convert_to_mib "$vnstat_eth1_tx" "$unit_eth1_tx")
# echo "convert_to_mib vnstat_eth0_tx unit_eth0_tx : ${vnstat_eth1_tx_pre}"
# sleep 10

# echo "HERE1"
# sleep 5

while true; do
    timestamp=$(date "+%Y-%m-%d %H:%M:%S")

    # CPU statistics with top
    cpu_us=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}')
    cpu_sys=$(top -bn1 | grep "Cpu(s)" | awk '{print $4}')
    cpu_usage=$(echo "$cpu_us + $cpu_sys" | bc)

    # RAM statistics with top
    # ram_usage=$(top -bn1 | grep "MiB Mem" | awk '{print $8}')
    ram_usage=$(( $(cat /sys/fs/cgroup/memory.current) / 1048576 ))

    # Ottieni statistiche di rete con sar
    # sar_eth0_rx=$(sar -n DEV 1 1 | grep "$network_interface_eth0" | awk '/Average/ {print ($5/1024)}')    
    # sar_eth0_tx=$(sar -n DEV 1 1 | grep "$network_interface_eth0" | awk '/Average/ {print ($6/1024)}')    
    # sar_eth1_rx=$(sar -n DEV 1 1 | grep "$network_interface_eth1" | awk '/Average/ {print ($5/1024)}')
    # sar_eth1_tx=$(sar -n DEV 1 1 | grep "$network_interface_eth1" | awk '/Average/ {print ($6/1024)}')

    # echo "HERE2"
    # sleep 5

    # # Network statistics with vnstat
    vnstat_eth0_rx=$(vnstat | awk '/^ eth0/ {getline; print $2}')
    # echo "vnstat | awk eth0 getline; print 2 : ${vnstat_eth0_rx}"
    # sleep 10
    unit_eth0_rx=$(vnstat | awk '/^ eth0/ {getline; print $3}')
    # echo "vnstat | awk eth0 getline; print 3 : ${unit_eth0_rx}"
    # sleep 10
    vnstat_eth0_rx=$(convert_to_mib "$vnstat_eth0_rx" "$unit_eth0_rx")
    # echo "convert_to_mib vnstat_eth0_rx unit_eth0_rx : ${vnstat_eth0_rx}"
    # sleep 10
    # vnstat_eth0_rx=$(echo "$vnstat_eth0_rx - $vnstat_eth0_rx_pre" | bc)
    # echo "echo vnstat_eth0_rx - vnstat_eth0_rx_pre | bc : ${vnstat_eth0_rx}"
    # sleep 10

    # echo "HERE3"
    # sleep 5

    vnstat_eth0_tx=$(vnstat | awk '/^ eth0/ {getline; print $5}')
    # echo "vnstat | awk eth0 getline; print 2 : ${vnstat_eth0_tx}"
    # sleep 10
    unit_eth0_tx=$(vnstat | awk '/^ eth0/ {getline; print $6}')
    # echo "vnstat | awk eth0 getline; print 3 : ${unit_eth0_tx}"
    # sleep 10
    vnstat_eth0_tx=$(convert_to_mib "$vnstat_eth0_tx" "$unit_eth0_tx")
    # echo "convert_to_mib vnstat_eth0_tx unit_eth0_tx : ${vnstat_eth0_tx}"
    # sleep 10
    # vnstat_eth0_tx=$(echo "$vnstat_eth0_tx - $vnstat_eth0_tx_pre" | bc)
    # echo "echo vnstat_eth0_rx - vnstat_eth0_tx_pre | bc : ${vnstat_eth0_tx}"
    # sleep 10

    # echo "HERE4"
    # sleep 5

    vnstat_eth1_rx=$(vnstat | awk '/^ eth1/ {getline; print $2}')
    unit_eth1_rx=$(vnstat | awk '/^ eth1/ {getline; print $3}')
    vnstat_eth1_rx=$(convert_to_mib "$vnstat_eth1_rx" "$unit_eth1_rx")
    # vnstat_eth1_rx=$(echo "$vnstat_eth1_rx - $vnstat_eth1_rx_pre" | bc)

    vnstat_eth1_tx=$(vnstat | awk '/^ eth1/ {getline; print $5}')
    unit_eth1_tx=$(vnstat | awk '/^ eth1/ {getline; print $6}')
    vnstat_eth1_tx=$(convert_to_mib "$vnstat_eth1_tx" "$unit_eth1_tx")
    # vnstat_eth1_tx=$(echo "$vnstat_eth1_tx - $vnstat_eth1_tx_pre" | bc)

    # echo "HERE5"
    # sleep 5

    # vnstat_eth0_rx_pre=$vnstat_eth0_rx
    # echo "vnstat_eth0_rx_pre: $vnstat_eth0_rx_pre"
    # sleep 10
    # vnstat_eth0_tx_pre=$vnstat_eth0_tx
    # vnstat_eth1_rx_pre=$vnstat_eth1_rx
    # vnstat_eth1_tx_pre=$vnstat_eth1_tx      

    # echo "HERE6"
    # sleep 5

    echo "\"$timestamp\",$cpu_usage,$ram_usage,$vnstat_eth0_rx,$vnstat_eth0_tx,$vnstat_eth1_rx,$vnstat_eth1_tx" >> "$output_file"
done &