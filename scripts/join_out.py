import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
import sys
import re
import time
import hashlib

# Definizione del DataFrame
df = pd.DataFrame()

# Percorso ai risultati
results_path = "results"

# Trova tutti i file "bench-results.csv" nelle sottocartelle di results
for root, dirs, files in os.walk(results_path):
    for file in files:
        if file == "bench-results.csv":            
            file_path = os.path.join(root, file)
            
            # Definisci il pattern regex per trovare la prima parola dopo "results/" e prima del primo trattino "-"
            pattern = r"results/([^\/-]+)-"
            match = re.search(pattern, file_path)
            if match:
                blockchain = match.group(1)
                # print(parola)
            else:
                print("Nessun match trovato")   
                print(root)
                continue
            
            tmp_df = pd.read_csv(file_path)
            tmp_df['blockchain'] = blockchain       
                    
            tmp_df['MiB-Rx'] = 0.0
            tmp_df['MiB-Tx'] = 0.0

            quantile_dir = os.path.join(os.path.dirname(root), 'img')
            # Loop through each value ('vnstat-eth0-Rx(MiB-s)' and 'vnstat-eth0-Tx(MiB-s)')
            for value in ['vnstat-eth0-Rx(MiB-s)', 'vnstat-eth0-Tx(MiB-s)']:
                # Loop through each workload
                for workload in tmp_df['workload'].unique():
                    # Check if the quantile file exists
                    quantile_file = os.path.join(quantile_dir, f'quantiles-{value}-{workload}.csv')
                    if os.path.exists(quantile_file):
                        # Read the CSV file into a DataFrame
                        var_df = pd.read_csv(quantile_file)
                        # Calculate the mean of all columns except 'Timestamp'
                        var_df_mean = var_df.drop(columns=['Timestamp']).mean(axis=1)
                        # Calculate MiB per second
                        if workload == '10000':
                            time_workload = 120.0
                        elif workload == 'dota':
                            time_workload = 276.0
                        elif workload == 'football':
                            time_workload = 100.0
                        elif workload == 'gafam':
                            time_workload = 180.0
                        elif workload == 'visa' or workload == 'paypal':
                            time_workload = 300.0            
                        mib_per_sec = var_df_mean.iloc[-1] / time_workload
                        # Update 'MiB-Rx' or 'MiB-Tx' column based on the value
                        if 'Rx' in value:
                            tmp_df.loc[tmp_df['workload'] == workload, 'MiB-Rx'] = mib_per_sec
                        else:
                            tmp_df.loc[tmp_df['workload'] == workload, 'MiB-Tx'] = mib_per_sec
                    
                    var_df_mean = var_df.drop(columns=['Timestamp']).mean(axis=1)
                    # Calculate MiB per second
                    if workload == '10000':
                        time_workload = 120.0
                    elif workload == 'dota':
                        time_workload = 276.0
                    elif workload == 'football':
                        time_workload = 100.0
                    elif workload == 'gafam':
                        time_workload = 180.0
                    elif workload == 'visa' or workload == 'paypal':
                        time_workload = 300.0            
                    mib_per_sec = var_df_mean.iloc[-1] / time_workload
                    # Update 'MiB-Rx' or 'MiB-Tx' column based on the value
                    if 'Rx' in value:
                        tmp_df.loc[tmp_df['workload'] == workload, 'MiB-Rx'] = mib_per_sec
                    else:
                        tmp_df.loc[tmp_df['workload'] == workload, 'MiB-Tx'] = mib_per_sec     
                        
            energy_dir = os.path.join(os.path.dirname(root), 'energy')
            # workloads = ['paypal', 'football']
            tmp_df['energy'] = 0.0
            # Loop through each workload
            for workload in tmp_df['workload'].unique():
                for index, row in tmp_df[tmp_df['workload'] == workload].iterrows():
                    start_time = row['start_bench']
                    if start_time == '0':
                        continue
                    else:
                        start_time = pd.to_datetime(start_time)
                    # end_time = None
                    
                    # Determine end_time based on the workload and blockchain
                    if workload == 'paypal':
                        if blockchain == 'algorand':
                            end_time = start_time + pd.Timedelta(seconds=300+30)
                        elif blockchain == 'diem':
                            end_time = start_time + pd.Timedelta(seconds=300+30)
                        elif blockchain == 'solana':
                            end_time = start_time + pd.Timedelta(seconds=300+30)
                        elif blockchain == 'poa':
                            end_time = start_time + pd.Timedelta(seconds=300+30)
                        elif blockchain == 'quorum':
                            end_time = start_time + pd.Timedelta(seconds=300+30)
                            
                    elif workload == 'football':
                        if blockchain == 'algorand':
                            end_time = start_time + pd.Timedelta(seconds=100+30)
                        elif blockchain == 'diem':
                            end_time = start_time + pd.Timedelta(seconds=100+30)
                        elif blockchain == 'solana':
                            end_time = start_time + pd.Timedelta(seconds=100+30)
                        elif blockchain == 'poa':
                            end_time = start_time + pd.Timedelta(seconds=100+30)
                        elif blockchain == 'quorum':
                            end_time = start_time + pd.Timedelta(seconds=100+30)
                            
                    elif workload == '10000':
                        if blockchain == 'algorand':
                            end_time = start_time + pd.Timedelta(seconds=120+30)
                        elif blockchain == 'diem':
                            end_time = start_time + pd.Timedelta(seconds=120+30)
                        elif blockchain == 'solana':
                            end_time = start_time + pd.Timedelta(seconds=120+30)
                        elif blockchain == 'poa':
                            end_time = start_time + pd.Timedelta(seconds=120+30)
                        elif blockchain == 'quorum':
                            end_time = start_time + pd.Timedelta(seconds=120+30)
                            
                    elif workload == 'gafam':
                        if blockchain == 'algorand':
                            end_time = start_time + pd.Timedelta(seconds=180+30)
                        elif blockchain == 'diem':
                            end_time = start_time + pd.Timedelta(seconds=180+30)
                        elif blockchain == 'solana':
                            end_time = start_time + pd.Timedelta(seconds=180+30)
                        elif blockchain == 'poa':
                            end_time = start_time + pd.Timedelta(seconds=180+30)
                        elif blockchain == 'quorum':
                            end_time = start_time + pd.Timedelta(seconds=180+30)    
                            
                    elif workload == 'dota':
                        if blockchain == 'algorand':
                            end_time = start_time + pd.Timedelta(seconds=276+30)
                        elif blockchain == 'diem':
                            end_time = start_time + pd.Timedelta(seconds=276+30)
                        elif blockchain == 'solana':
                            end_time = start_time + pd.Timedelta(seconds=276+30)
                        elif blockchain == 'poa':
                            end_time = start_time + pd.Timedelta(seconds=276+30)
                        elif blockchain == 'quorum':
                            end_time = start_time + pd.Timedelta(seconds=276+30)                                                           

                    elif workload == 'visa':
                        if blockchain == 'algorand':
                            end_time = start_time + pd.Timedelta(seconds=300+30)
                        elif blockchain == 'diem':
                            end_time = start_time + pd.Timedelta(seconds=300+30)
                        elif blockchain == 'solana':
                            end_time = start_time + pd.Timedelta(seconds=300+30)
                        elif blockchain == 'poa':
                            end_time = start_time + pd.Timedelta(seconds=300+30)
                        elif blockchain == 'quorum':
                            end_time = start_time + pd.Timedelta(seconds=300+30)    
                            
                    # print(end_time)   
                            
                    # print(tmp_df.loc[index])
                    
                    # Calculate the total energy consumed
                    energy_consumed = 0
                    energy_files = [f for f in os.listdir(energy_dir) if f.startswith('energy') and f.endswith('.csv')]
                    
                    for energy_file in energy_files:
                        energy_file_path = os.path.join(energy_dir, energy_file)
                        energy_df = pd.read_csv(energy_file_path)
                        
                        energy_df['Timestamp'] = pd.to_datetime(energy_df['Timestamp'])
                        
                        # print("START", start_time)                    
                        # print(energy_df[energy_df['Timestamp'] <= start_time].iloc[-1])
                        # print()
                        # print()
                        # print("END", end_time)
                        # print(energy_df[energy_df['Timestamp'] >= end_time])
                        # print()
                        # print()                 
                        # print(energy_df)
                        
                                                
                        start_row = energy_df[energy_df['Timestamp'] <= start_time].iloc[-1]
                        # print(tmp)                        
                        
                        # Get the intel-rapl value for end_time
                        
                        # print(energy_file_path)
                        # print(energy_df)
                        # print(energy_df[energy_df['Timestamp'] >= end_time])
                        # print(energy_df[energy_df['Timestamp'] >= end_time].iloc[0])                        
                        
                        if energy_df['Timestamp'].iloc[-1] < end_time:
                            end_row = energy_df.iloc[-1]
                        else:
                            end_row = energy_df[energy_df['Timestamp'] >= end_time].iloc[0]                                                
                            
                        # INTEL RAPL
                        start_energy = start_row['intel-rapl']    
                        end_energy = end_row['intel-rapl']
                        
                        # Calculate the energy consumed for this file
                        energy_consumed += (end_energy - start_energy)/ 1000000
                        
                        
                        # # PERF            
                        # energy_df = energy_df.iloc[start_row.name:end_row.name]                               
                        # perf_columns_sum = 0
                        # for col in energy_df.columns:
                        #     if 'power' in col:
                        #         column_sum = energy_df[col].sum()
                        #         perf_columns_sum += column_sum                  
                        # if energy_consumed == 0:
                        #     energy_consumed = perf_columns_sum
                        # else:
                        #     energy_consumed = (energy_consumed+perf_columns_sum)                  
                    
                    tmp_df.loc[index, 'energy'] = energy_consumed * 2.7778e-7
                    # print(tmp_df)
                
            df = pd.concat([df, tmp_df], ignore_index=True)

# print(df)

# df.to_csv("results/join-bench-results.csv", index=False)

# df = df[df['median_latency'] != 0.0]
cols_to_remove = ['delay', 'congestion']
df.drop(columns=cols_to_remove, inplace=True)   
if 'dynamic' in df.columns:
    df['dynamic'] = df['dynamic'].fillna(0).astype(int)
if 'bandwidth' in df.columns:
    df['bandwidth'] = df['bandwidth'].fillna(0).astype(str)
if 'switch' in df.columns:
    df['switch'] = df['switch'].fillna(0).astype(int)
if 'latency' in df.columns:
    df['latency'] = df['latency'].fillna(0).astype(int)    

df['MiB-Rx'] = df['MiB-Rx'].fillna(0.0)
df['MiB-Tx'] = df['MiB-Tx'].fillna(0.0)

# Arrotonda i valori a due cifre decimali
df['MiB-Rx'] = df['MiB-Rx'].round(2)
df['MiB-Tx'] = df['MiB-Tx'].round(2)

# Salva il DataFrame in un file CSV
df.to_csv("results/join-bench-results.csv", index=False)



# SECOND SET EXPERIMENTS
df = pd.DataFrame()

results_path = "results/new"

for root, dirs, files in os.walk(f"{results_path}"):
    for file in files:
        if file == "bench-results.csv":           
            file_path = os.path.join(root, file)
                    
            pattern = rf"{results_path}/([^\/-]+)-"
            match = re.search(pattern, file_path)
            if match:
                blockchain = match.group(1)
                # print(parola)
            else:
                print("No match found")   
                print(root)
                continue
            
            # match = re.search(r'bandwidth([0-9.]+)-', file_path)
            # if match:
            #     bandwidth = match.group(1)
                # # Convertire a float se c'è un punto, altrimenti a int
                # if '.' in bandwidth:
                #     bandwidth = float(bandwidth)
                # else:
                #     bandwidth = int(bandwidth)  
                #     print(bandwidth)                              
            
            tmp_df = pd.read_csv(file_path)
            tmp_df['blockchain'] = blockchain  
            # tmp_df['bandwidth'] = bandwidth                 
                    
            tmp_df['MiB-Rx'] = 0.0
            tmp_df['MiB-Tx'] = 0.0
            
            # if tmp_df['start_bench'].iloc[0] == 0:
            #     tmp_df[['commit_number', 'average_throughput', 'average_load', 'average_latency']] = 9999999999999999

            quantile_dir = os.path.join(os.path.dirname(root), 'img')
            # Loop through each value ('vnstat-eth0-Rx(MiB-s)' and 'vnstat-eth0-Tx(MiB-s)')
            for value in ['vnstat-eth0-Rx(MiB-s)', 'vnstat-eth0-Tx(MiB-s)']:
                # Loop through each workload
                for workload in tmp_df['workload'].unique():
                    # Check if the quantile file exists
                    quantile_file = os.path.join(quantile_dir, f'quantiles-{value}-{workload}.csv')
                    if os.path.exists(quantile_file):
                        # Read the CSV file into a DataFrame
                        var_df = pd.read_csv(quantile_file)
                        # Calculate the mean of all columns except 'Timestamp'
                        var_df_mean = var_df.drop(columns=['Timestamp']).mean(axis=1)
                        # Calculate MiB per second
                        if workload == '10000':
                            time_workload = 120.0
                        elif workload == 'dota':
                            time_workload = 276.0
                        elif workload == 'football':
                            time_workload = 100.0
                        elif workload == 'gafam':
                            time_workload = 180.0
                        elif workload == 'visa' or workload == 'paypal':
                            time_workload = 300.0            
                        mib_per_sec = var_df_mean.iloc[-1] / time_workload
                        # Update 'MiB-Rx' or 'MiB-Tx' column based on the value
                        if 'Rx' in value:
                            tmp_df.loc[tmp_df['workload'] == workload, 'MiB-Rx'] = mib_per_sec
                        else:
                            tmp_df.loc[tmp_df['workload'] == workload, 'MiB-Tx'] = mib_per_sec
                            
            energy_dir = os.path.join(os.path.dirname(root), 'energy')
            workloads = ['paypal', 'football']
            tmp_df['energy'] = 0.0
            # Loop through each workload
            for workload in workloads:
                for index, row in tmp_df[tmp_df['workload'] == workload].iterrows():
                    start_time = row['start_bench']
                    if start_time == '0':
                        continue
                    else:
                        start_time = pd.to_datetime(start_time)
                    # end_time = None
                    
                    # Determine end_time based on the workload and blockchain
                    if workload == 'paypal':
                        if blockchain == 'algorand':
                            end_time = start_time + pd.Timedelta(seconds=350)
                        elif blockchain == 'diem':
                            end_time = start_time + pd.Timedelta(seconds=350)
                        elif blockchain == 'solana':
                            end_time = start_time + pd.Timedelta(seconds=350)
                        elif blockchain == 'poa':
                            end_time = start_time + pd.Timedelta(seconds=350)
                        elif blockchain == 'quorum':
                            end_time = start_time + pd.Timedelta(seconds=350)
                            
                    elif workload == 'football':
                        if blockchain == 'algorand':
                            end_time = start_time + pd.Timedelta(seconds=150)
                        elif blockchain == 'diem':
                            end_time = start_time + pd.Timedelta(seconds=150)
                        elif blockchain == 'solana':
                            end_time = start_time + pd.Timedelta(seconds=150)
                        elif blockchain == 'poa':
                            end_time = start_time + pd.Timedelta(seconds=150)
                        elif blockchain == 'quorum':
                            end_time = start_time + pd.Timedelta(seconds=150)
                            
                    # print(tmp_df.loc[index])
                    
                    # Calculate the total energy consumed
                    energy_consumed = 0
                    energy_files = [f for f in os.listdir(energy_dir) if f.startswith('energy') and f.endswith('.csv')]
                    
                    for energy_file in energy_files:
                        energy_file_path = os.path.join(energy_dir, energy_file)
                        energy_df = pd.read_csv(energy_file_path)
                        
                        energy_df['Timestamp'] = pd.to_datetime(energy_df['Timestamp'])
                        
                        # print("START", start_time)                    
                        # print(energy_df[energy_df['Timestamp'] <= start_time].iloc[-1])
                        # print()
                        # print()
                        # print("END", end_time)
                        # print(energy_df[energy_df['Timestamp'] >= end_time])
                        # print()
                        # print()                 
                        # print(energy_df)
                        
                        # Get the intel-rapl value for start_time
                        start_row = energy_df[energy_df['Timestamp'] <= start_time].iloc[-1]
                        # print(tmp)
                        start_energy = start_row['intel-rapl']
                        
                        # Get the intel-rapl value for end_time
                        end_row = energy_df[energy_df['Timestamp'] >= end_time].iloc[0]
                        end_energy = end_row['intel-rapl']
                        
                        # Calculate the energy consumed for this file
                        energy_consumed += (end_energy - start_energy)/1000000
                    
                    tmp_df.loc[index, 'energy'] = energy_consumed
                    # print(tmp_df)                            
                            
                
            df = pd.concat([df, tmp_df], ignore_index=True)

            # print(df)

# df = df[df['median_latency'] != 0.0]
# cols_to_remove = ['delay', 'congestion']
# df.drop(columns=cols_to_remove, inplace=True)   
# if 'dynamic' in df.columns:
#     df['dynamic'] = df['dynamic'].fillna(0).astype(int)
# if 'bandwidth' in df.columns:
#     df['bandwidth'] = df['bandwidth'].fillna(0).astype(str)
# if 'switch' in df.columns:
#     df['switch'] = df['switch'].fillna(0).astype(int)

df['MiB-Rx'] = df['MiB-Rx'].fillna(0.0)
df['MiB-Tx'] = df['MiB-Tx'].fillna(0.0)

df['MiB-Rx'] = df['MiB-Rx'].round(2)
df['MiB-Tx'] = df['MiB-Tx'].round(2)

df.to_csv("results/new/join-bench-results.csv", index=False)



# DYNAMIC EXPERIMENTS
results_path = "results/dynamic"
dynamics = ["packet-drop", "bw-congestion", "node-crash"]
size_of_dynamics = ["30", "10", "20"]


for folder in dynamics:                    
    path = f"{results_path}/{folder}"

    if os.path.exists(path):        
                    
        df = pd.DataFrame()    

        for size in size_of_dynamics:
            
            path = f"{results_path}/{folder}/{size}"

            if os.path.exists(path):            
                for root, dirs, files in os.walk(path):        
                    for file in files:
                        if file == "bench-results.csv":           
                            file_path = os.path.join(root, file)
                            
                            pattern = rf"{results_path}/{folder}/{size}/([^\/-]+)-"
                            match = re.search(pattern, file_path)
                            if match:
                                blockchain = match.group(1)
                                # print(parola)
                            else:
                                print("No match found")   
                                print(root)
                                continue
                            
                            tmp_df = pd.read_csv(file_path)
                            tmp_df['blockchain'] = blockchain     
                            tmp_df['dynamic'] = size
                                    
                            tmp_df['MiB-Rx'] = 0.0
                            tmp_df['MiB-Tx'] = 0.0

                            quantile_dir = os.path.join(os.path.dirname(root), 'img')
                            # Loop through each value ('vnstat-eth0-Rx(MiB-s)' and 'vnstat-eth0-Tx(MiB-s)')
                            for value in ['vnstat-eth0-Rx(MiB-s)', 'vnstat-eth0-Tx(MiB-s)']:
                                # Loop through each workload
                                for workload in tmp_df['workload'].unique():
                                    # Check if the quantile file exists
                                    quantile_file = os.path.join(quantile_dir, f'quantiles-{value}-{workload}.csv')
                                    if os.path.exists(quantile_file):
                                        # Read the CSV file into a DataFrame
                                        var_df = pd.read_csv(quantile_file)
                                        # Calculate the mean of all columns except 'Timestamp'
                                        var_df_mean = var_df.drop(columns=['Timestamp']).mean(axis=1)
                                        # Calculate MiB per second
                                        if workload == '10000':
                                            time_workload = 120.0
                                        elif workload == 'dota':
                                            time_workload = 276.0
                                        elif workload == 'football':
                                            time_workload = 100.0
                                        elif workload == 'gafam':
                                            time_workload = 180.0
                                        elif workload == 'visa' or workload == 'paypal':
                                            time_workload = 300.0            
                                        mib_per_sec = var_df_mean.iloc[-1] / time_workload
                                        # Update 'MiB-Rx' or 'MiB-Tx' column based on the value
                                        if 'Rx' in value:
                                            tmp_df.loc[tmp_df['workload'] == workload, 'MiB-Rx'] = mib_per_sec
                                        else:
                                            tmp_df.loc[tmp_df['workload'] == workload, 'MiB-Tx'] = mib_per_sec
                                
                            df = pd.concat([df, tmp_df], ignore_index=True)

        # df = df[df['median_latency'] != 0.0]
        # cols_to_remove = ['delay', 'congestion']
        # df.drop(columns=cols_to_remove, inplace=True)   
        if 'dynamic' in df.columns:
            df['dynamic'] = df['dynamic'].fillna(0).astype(int)
        if 'bandwidth' in df.columns:
            df['bandwidth'] = df['bandwidth'].fillna(0).astype(str)
        if 'switch' in df.columns:
            df['switch'] = df['switch'].fillna(0).astype(int)

        df['MiB-Rx'] = df['MiB-Rx'].fillna(0.0)
        df['MiB-Tx'] = df['MiB-Tx'].fillna(0.0)

        df['MiB-Rx'] = df['MiB-Rx'].round(2)
        df['MiB-Tx'] = df['MiB-Tx'].round(2)

        joined_df = pd.read_csv("results/join-bench-results.csv")
        joined_df = joined_df[joined_df['mode'] == 'full-mesh']    
        joined_df = joined_df[joined_df['dataset'] == 'diablo']
        joined_df = joined_df[joined_df['workload'] == 'paypal']
        joined_df = joined_df[joined_df['link_strategy'] == 'hop']
        joined_df = joined_df[joined_df['network_size'] == 1]
        joined_df = joined_df[joined_df['secondaries'] == 10]
        joined_df = joined_df[joined_df['cores'] == 8]
        joined_df = joined_df[joined_df['ram'] == 16]
        joined_df = joined_df[joined_df['dynamic'] == 0]

        df = pd.concat([df, joined_df], ignore_index=True)
        df.to_csv(f"{results_path}/{folder}/dynamics-bench-results.csv", index=False)