#!/bin/bash


terminate_child_processes() {
    echo "Terminating SSH multiplexing..."
    for machine in "${machines[@]}"; do
      (        
        ssh -O exit "$machine"
      ) &
    done      
    wait 
    
    pkill -P $$ 
}

trap 'terminate_child_processes' EXIT SIGINT SIGTERM KILL


# implementations=("quorum" "poa" "algorand" "diem" "solana")
implementations=("diem" "solana")


# dynamics=(0 1 2 3 4 5)
# dynamics=(1 2 4)
dynamics=(1 4)

# rams=(16)
# rams=(2)
# cores=(8)
# cores=(1)

secondaries=(10)

# link_strategies=("latency" "hop")
link_strategies=("hop")

# datasets=("our" "diablo")
datasets=("diablo")

# modes=('full-mesh' 'scale-free-t' 'scale-free-l' 'scale-free-r' 'double-l' 'double-s' 'torus-l' 'torus-t' 'torus-r' 'fat-tree-t' 'fat-tree-l' 'hypercube')
# modes=('full-mesh' 'scale-free-l' 'torus-l' 'fat-tree-l' 'hypercube')
modes=('full-mesh')

# sizes=(1 4)
sizes=(1)

# switches=(250 500 1000)
switches=(0)

# bandwidths=(0.1 1)
bandwidths=(1)

# latencies=(25 50 100)
latencies=(0)

repetitions=2


# latency check
net_check=0
declare -A check
keys=('full-mesh' 'scale-free-t' 'scale-free-l' 'scale-free-r' 'double-l' 'double-s' 'torus-l' 'torus-t' 'torus-r' 'fat-tree-t' 'fat-tree-l' 'hypercube')
for key in "${keys[@]}"; do
    check["$key"]=0
done


for implementation in "${implementations[@]}"; do
    for mode in "${modes[@]}"; do

        if [ "$net_check" -eq 1 ] && [ "${check["$mode"]}" -eq 0 ]; then
            check["$mode"]=1
            check_exec=1
        else
            check_exec=0
        fi

        for secondary in "${secondaries[@]}"; do
            for size in "${sizes[@]}"; do
                for strategy in "${link_strategies[@]}"; do
                    for dataset in "${datasets[@]}"; do  
                        for dynamic in "${dynamics[@]}"; do       
                            for bandwidth in "${bandwidths[@]}"; do   
                                for switch in "${switches[@]}"; do           
                                    for latency in "${latencies[@]}"; do                               
                                        echo "#######################################################"
                                        echo "-------------------------------------------------------"
                                        echo "*******************************************************"
                                        echo "implementation:${implementation}"
                                        echo "mode:${mode}"
                                        echo "secondary:${secondary}"
                                        echo "size:${size}"
                                        echo "dataset:${dataset}"
                                        echo "link strategy:${strategy}"
                                        echo "network check:${check_exec}"
                                        echo "bandwidth:${bandwidth}"
                                        echo "dynamic:${dynamic}"
                                        echo "switch:${switch}"
                                        echo "latency:${latency}"
                                        echo "-------------------------------------------------------"
                                        echo "#######################################################"

                                        for ((repetition=1; repetition<=$repetitions; repetition++)); do
                                            ./run.sh -i "$implementation" -s "$secondary" -m "$mode" --size "$size" --dataset "$dataset" -l "$strategy" --check "$check_exec" --dynamic "$dynamic" --switch "$switch" -b "$bandwidth" --latency "$latency"
                                        done                                    

                                        echo "DONE"
                                        echo ""
                                        echo ""
                                    done
                                done
                            done
                        done
                    done
                done
            done
        done
    done
done

set +e
python3 scripts/join_out.py