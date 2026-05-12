import pandas as pd
import os
import sys
import re
import time
import hashlib
import matplotlib.pyplot as plt
import numpy as np


if len(sys.argv) != 2:
    print("Usage: python script.py <directory_path>")
    sys.exit(1)

directory_path = sys.argv[1]

file_path = "/tmp/run.tmp"
try:
    with open(file_path, 'r') as file:
        content = file.read()
        print("Contenuto del file:", content)
        
        content = content.strip()
        tmp_values = content.split('-')
        implementation = tmp_values[0]
        # print(implementation)
        cores = tmp_values[1]
        cores = int(cores.replace('cores', ''))
        # print(cores)
        ram = tmp_values[2]
        ram = int(ram.replace('ram', ''))
        # print(ram)
        secondaries = tmp_values[3]
        secondaries = int(secondaries.replace('secondaries', ''))
        # print(secondaries)
        bandwidth = tmp_values[4]        
        bandwidth = bandwidth.replace('bandwidth', '')
        # if '.' in bandwidth:
        #     bandwidth = float(bandwidth)
        # else:
        #     bandwidth = int(bandwidth)
        # print(bandwidth)        
        dataset = tmp_values[5]        
        dataset = dataset.replace('dataset:', '')
        # print(dataset)                
        network_size = tmp_values[6]
        network_size = int(network_size.replace('size', ''))
        # print(network_size)
        strategy = tmp_values[7]        
        strategy = strategy.replace('strategy:', '')
        # print(strategy)      
        dynamic = tmp_values[8]        
        dynamic = dynamic.replace('dynamic:', '')
        # print(dynamic)                        
        switch = tmp_values[9]        
        switch = switch.replace('switch:', '')
        # print(switch)                       
        latency = tmp_values[10]        
        latency = latency.replace('latency:', '')
        # print(latency)                                        
        mode = '-'.join(tmp_values[11:]) if len(tmp_values) > 11 else ''     
        # print(mode)   
except FileNotFoundError:
    print("Il file", file_path, "non è stato trovato.")
avg_df = pd.DataFrame(columns=['hash', 'workload', 'bandwidth', 'switch', 'latency', 'run', 'mode', 'dataset', 'link_strategy', 'cores', 'ram', 'secondaries', 'network_size', 'dynamic', 'submit_number', 'commit_number', 'abort_number', 'average_load', 'average_throughput', 'average_latency', 'median_latency', 'start_bench'])

# Itero nella sotto-cartella "workloads"
for subdir in os.listdir(os.path.join(directory_path, "workloads")):
    # Ottieni il nome del workload
    workload_name = subdir
    # print(workload_name)
    
    # Inizializzo il numero di run
    # run = 0

    workload_with_timestamp = f"{workload_name}-{int(time.time())}"
    hash_object = hashlib.sha256(workload_with_timestamp.encode())
    workload_hash = hash_object.hexdigest()[:6]    
    
    # Inizializza le variabili
    submit_number = None
    commit_number = None
    abort_number = None
    average_load = None
    average_throughput = None
    average_latency = None
    median_latency = None    
    
    # Percorso della cartella del workload
    workload_folder = os.path.join(directory_path, "workloads", subdir)
    # print(workload_folder)
    
    # Cerco i file "out" nella sottocartella
    for root, dirs, _ in os.walk(workload_folder):
        for run in dirs:
            subdir_path = os.path.join(root, run)
            # print(int(run.split('/')[-1]))
            run = int(run)            
            for filename in os.listdir(subdir_path):
                if "err" in filename:
                    file_path = os.path.join(subdir_path, filename)                                              

                    # Legge il contenuto del file err
                    with open(file_path, "r") as file:
                        start = None
                        for line in file:
                            if "start benchmark" in line:
                                match = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3})", line)
                                if match:
                                    start = match.group(0)
                                    print(f"Start Bench: {start}")
                                    break                      
                        if not start:
                            print("Primary didn't start")
                            #fake start
                            start = "0"                                       
                elif "out" in filename:
                    file_path = os.path.join(subdir_path, filename)
                    # run += 1
                    # print("Filepath: ", filepath)
                    
                    # Apro il file e leggo le righe
                    with open(file_path, 'r') as file:
                        # # Se il file contiene una riga con "-", passo al prossimo file
                        # if "-" in file.read() or os.stat(file_path).st_size == 0:
                        #     print("File out no good : ", file_path)
                        #     continue
                        
                        # # Torno all'inizio del file
                        # file.seek(0)                        
                        
                        # Leggo ogni riga del file
                        for line in file:
                            # print("Line: ", line)
                            match = re.match(r'.*:\s*([\d.-]+)', line)
                            # print("Match: ", match)
                            if match:
                                if '-' in match.group(1):
                                    value = 0.0
                                else:
                                    value = float(match.group(1))
                                
                                # print("Value: ", value)                            
                                
                                if "submit number" in line:
                                    submit_number = value                                    
                                elif "commit number" in line:
                                    commit_number = value
                                elif "abort number" in line:
                                    abort_number = value                                    
                                elif "average load" in line:
                                    average_load = value                                    
                                elif "average throughput" in line:
                                    average_throughput = value                                    
                                elif "average latency" in line:
                                    average_latency = value
                                elif "median latency" in line:
                                    median_latency = value
                                
                                # print(median_latency)  
                                # Aggiorno le variabili in base al contenuto delle righe
                                # if "submit number" in line:
                                #     if submit_number is None:
                                #         submit_number = value
                                #     else:
                                #         submit_number = (submit_number + value) / 2
                                # elif "commit number" in line:
                                #     if commit_number is None:
                                #         commit_number = value
                                #     else:
                                #         commit_number = (commit_number + value) / 2
                                # elif "abort number" in line:
                                #     if abort_number is None:
                                #         abort_number = value
                                #     else:
                                #         abort_number = (abort_number + value) / 2
                                # elif "average load" in line:
                                #     if average_load is None:
                                #         average_load = value
                                #     else:
                                #         average_load = (average_load + value) / 2
                                # elif "average throughput" in line:
                                #     if average_throughput is None:
                                #         average_throughput = value
                                #     else:
                                #         average_throughput = (average_throughput + value) / 2
                                # elif "average latency" in line:
                                #     if average_latency is None:
                                #         average_latency = value
                                #     else:
                                #         average_latency = (average_latency + value) / 2
                                # elif "median latency" in line:
                                #     if median_latency is None:
                                #         median_latency = value
                                #     else:
                                #         median_latency = (median_latency + value) / 2
                        # print(median_latency)                                    
                        # print("Filepath: ", file_path)
    
            # print(median_latency)
            new_row = pd.DataFrame([[workload_hash, str(workload_name), bandwidth, switch, latency, run, mode, dataset, strategy, cores, ram, secondaries, network_size, dynamic, submit_number, commit_number, abort_number, average_load, average_throughput, average_latency, median_latency, start]], columns=['hash', 'workload', 'bandwidth', 'switch', 'latency', 'run', 'mode', 'dataset', 'link_strategy', 'cores', 'ram', 'secondaries', 'network_size', 'dynamic', 'submit_number', 'commit_number', 'abort_number', 'average_load', 'average_throughput', 'average_latency', 'median_latency', 'start_bench'])
            avg_df = pd.concat([avg_df, new_row], ignore_index=True)
    
avg_df[['switch', 'latency', 'cores', 'ram', 'dynamic', 'secondaries', 'network_size', 'submit_number', 'commit_number', 'abort_number']] = avg_df[['switch', 'latency', 'cores', 'ram', 'dynamic', 'secondaries', 'network_size', 'submit_number', 'commit_number', 'abort_number']].fillna(0).astype(int)
avg_df[['average_load', 'average_throughput', 'average_latency', 'median_latency']] = avg_df[['average_load', 'average_throughput', 'average_latency', 'median_latency']].fillna(0).round(2)
print(avg_df)

avg_df.to_csv("/results/bench-results.csv", index=False)
