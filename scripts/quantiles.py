import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
import sys
import re
import time

# Prendere in input una directory
# Verifica se è stato fornito il percorso della cartella come argomento
if len(sys.argv) != 2:
    print("Usage: python script.py <directory_path>")
    sys.exit(1)

directory_path = sys.argv[1]

cartella_primary = next(folder for folder in os.listdir(directory_path) if 'primary' in folder)
bench_csv = pd.read_csv(f"{directory_path}/{cartella_primary}/bench-results.csv")

# rimosso CPU-Usage
# columns = ["RAM Usage(MB)", "vnstat-eth0-Rx(MiB/s)", "vnstat-eth0-Tx(MiB/s)", "vnstat-eth1-Rx(MiB/s)", "vnstat-eth1-Tx(MiB/s)"]
# columns = ["RAM Usage(MB)", "vnstat-eth0-Rx(MiB-s)", "vnstat-eth0-Tx(MiB-s)", "vnstat-eth1-Rx(MiB-s)", "vnstat-eth1-Tx(MiB-s)"]
columns = ["RAM Usage(MB)", "vnstat-eth0-Rx(MiB-s)", "vnstat-eth0-Tx(MiB-s)"]
# workloads = ["10000", "gafam", "dota", "football", "visa", "paypal"]
# regions = ['af-south-1', 'ap-northeast-1', 'ap-south-1', 'ap-southeast-2', 'eu-north-1', 'eu-south-1', 'me-south-1', 'sa-east-1', 'us-east-2', 'us-west-2']   

for col in columns:
    # combined_df = pd.DataFrame()
    print(col)
    
    for workload in bench_csv['workload'].unique():
        combined_df = pd.DataFrame()
        print(workload)

        runs = bench_csv.loc[bench_csv['workload'] == workload, 'run'].max()                
        
        # Single region task
        for directory in os.listdir(directory_path):
            
            if all(item not in directory for item in ["secondary", "primary", "energy", "img", "logs"]):                            
                pattern = r"kollaps_(.+?)-n\d+-"
                match = re.search(pattern, directory)
                if match:
                    region_name = match.group(1)                    
                    # print(region_name)
                    region_combined = pd.DataFrame()                    
                    # dfs = []
                    
                    invalid_run=0
                    for run in range(1, runs + 1):
                        start = bench_csv.loc[(bench_csv['workload'] == workload) & (bench_csv['run'] == run), 'start_bench'].iloc[0] 
                        # if start and bench_csv.loc[(bench_csv['start_bench'] == start), 'average_latency'].iloc[0] != 0.0:
                        if start:
                            start = pd.to_datetime(start).floor('s')
                            region_dir_run_csv = os.path.join(directory_path, directory, "workloads", workload, str(run), "resources_stats.csv")
                            region_run_csv=pd.read_csv(region_dir_run_csv)                                            
                            region_run_csv['Timestamp'] = pd.to_datetime(region_run_csv['Timestamp']).dt.floor('s')

                            # Normalize the values in the Timestamp column based on their respective start variable.
                            region_run_csv['Timestamp'] = (region_run_csv['Timestamp'] - start).dt.total_seconds()
                            # print(region_run_csv)
                            # time.sleep(5)
                            
                            region_run_csv = region_run_csv[['Timestamp', col]]
                            # Filter the DataFrame to retain only the values from the start date until -10 seconds.
                            region_run_csv = region_run_csv[region_run_csv['Timestamp'] >= -20]    
                            region_run_csv = region_run_csv.groupby('Timestamp').mean().reset_index()                                            
                            # print(region_run_csv)
                            # time.sleep(5)
                            # region_run_csv.to_csv(f"{run}temp.csv", index=False)                                                
                            
                            if region_combined.empty:
                                region_combined = region_run_csv
                            else:
                                region_combined = pd.merge(region_combined, region_run_csv, on='Timestamp', how='outer')                            
                                                                                        
                                region_combined[col] = (region_combined[col+'_x'] + region_combined[col+'_y']) / 2
                                region_combined.drop([col+'_x', col+'_y'], axis=1, inplace=True)                  
                                region_combined = region_combined.dropna(subset=[col])
                        # else:
                        #     invalid_run += 1
                    
                    region_combined['Timestamp'] = region_combined['Timestamp'].astype(int)
                    region_combined[col] = region_combined[col].astype(int)

                    # if col == 'vnstat-eth0-Rx(MiB-s)' or col == 'vnstat-eth0-Tx(MiB-s)':
                    #     # Save the value of col in the first row
                    #     previous_val = region_combined.iloc[0, region_combined.columns.get_loc(col)]
                    #     print(previous_val)

                    #     # Iterate over each row starting from the second one
                    #     for i in range(1, len(region_combined)):
                    #         # Check if the value of col in the current row is different from the value saved in the previous row
                    #         if region_combined.iloc[i, region_combined.columns.get_loc(col)] == previous_val:
                    #             region_combined.iloc[i, region_combined.columns.get_loc(col)] = 0
                    #         else:
                    #             # Otherwise, update the previous value to the current value of col
                    #             previous_val = region_combined.iloc[i, region_combined.columns.get_loc(col)]
                    #             print(previous_val)

                    # print(region_combined)
                    # time.sleep(5)       
                    save_path = os.path.join(directory_path, directory, "workloads", workload, "merge-runs.csv")                            
                    region_combined.to_csv(save_path, index=False)                                                           
                    
                else:
                    print("No correspondence.")
                    print(directory)
                    exit(1)                          
                  
        start = 0
            
        for directory in os.listdir(directory_path):            
            if all(item not in directory for item in ["secondary", "primary", "energy", "img", "logs"]):                            
                pattern = r"kollaps_(.+?)-n\d+-"
                match = re.search(pattern, directory)
                if match:
                    region_name = match.group(1)
                    # print(region_name)
                else:
                    print("No correspondence.")
                    # exit(1)

                region_dir_run_csv = os.path.join(directory_path, directory, "workloads", workload, "merge-runs.csv")
                region_df = pd.read_csv(region_dir_run_csv)
                # print(region_df[col])
                # time.sleep(2)
                region_df = region_df.rename(columns={col: region_name})
                # print(region_df)
                # time.sleep(5)
                # print(region_df.columns)
                # time.sleep(5)
                region_df = region_df[['Timestamp', region_name]]
                
                if combined_df.empty:
                    combined_df = region_df                    
                else:
                    combined_df = pd.merge(combined_df, region_df[['Timestamp', region_name]], on='Timestamp', how='outer')                                                                   
                    if combined_df.filter(like=region_name).shape[1] > 1:                    
                        combined_df[region_name] = (combined_df[region_name+'_x'] + combined_df[region_name+'_y']) / 2
                        combined_df.drop([region_name+'_x', region_name+'_y'], axis=1, inplace=True)                  
                
                combined_df = combined_df.dropna(subset=[region_name])                    
                combined_df[region_name] = combined_df[region_name].astype(int)
        
        # print(combined_df.head(80))
        # combined_df.to_csv("withNA.csv", index=False)
        # Riempie i valori mancanti con i valori precedenti
        # Ordina il DataFrame per Timestamp
        combined_df = combined_df.sort_values(by='Timestamp')
        combined_df = combined_df.ffill()
        # print(combined_df.head(80))    
        # print(combined_df)
        combined_df.to_csv(f"{directory_path}/img/quantiles-{col}-{workload}.csv", index=False)
        
        # # Trova in combined_df dove il valore di 'Timestamp' è uguale a start e assegna a start_timestamp il valore di quella riga intera
        # # Verifica se il valore di start è presente nei timestamp di combined_df
        # if start not in combined_df['Timestamp'].values:
        #     print("Il timestamp di start non è presente nel DataFrame.")
        #     if start == "0":
        #         start = combined_df.iloc[0]['Timestamp']
        #     else:
        #         # Trova il timestamp più vicino e precedente a quello di start
        #         start = combined_df.loc[combined_df['Timestamp'] <= start, 'Timestamp'].max()
        #         # # Trova l'indice corrispondente al timestamp più vicino
        #         # start_index = combined_df.loc[combined_df['Timestamp'] == closest_timestamp].index[0]
        
        start_row = combined_df[combined_df['Timestamp'] == start].iloc[0]        

        # # Calcola il tempo totale trascorso in ogni intervallo di tempo
        # combined_df['Timestamp'] = pd.to_datetime(combined_df['Timestamp'])
        # combined_df['Timestamp'] = (combined_df['Timestamp'] - combined_df['Timestamp'].min()).dt.total_seconds()
        
        # Find start in the dataframe
        # start_row_match = combined_df.drop(columns=['Timestamp']).eq(start_row.drop('Timestamp'))                
        start_row_match = combined_df.eq(start_row)

        # get the index
        start_index = start_row_match.all(axis=1).idxmax()
        # print(start_index)

        start_timestamp = combined_df.loc[start_index, 'Timestamp']
        
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
            
        combined_df = combined_df[combined_df['Timestamp'] <= time_workload + 50]        

        # Percentiles calculation for all the regions
        percentiles = [25, 50, 75, 100]
        all_percentiles = pd.DataFrame(columns=['Timestamp'] + [f'{p}th Percentile' for p in percentiles])

        for idx, timestamp in enumerate(combined_df['Timestamp']):
            values_at_timestamp = combined_df.iloc[idx, 1:]  # Escludi la colonna 'Timestamp'
            percentile_values = [np.percentile(values_at_timestamp, p) for p in percentiles]
            all_percentiles.loc[idx] = [timestamp] + percentile_values

        plt.figure(figsize=(12, 6))

        # for p in percentiles:
        #     plt.plot(all_percentiles['Timestamp'], all_percentiles[f'{p}th Percentile'], label=f'{p}th Percentile')
            
        for i in range(len(percentiles) - 1):
            plt.fill_between(all_percentiles['Timestamp'], all_percentiles[f'{percentiles[i]}th Percentile'],
                            all_percentiles[f'{percentiles[i+1]}th Percentile'], label=f'{percentiles[i]}th to {percentiles[i+1]}th Percentiles', zorder=1)
            

        # # Salva il timestamp iniziale del benchmark nel formato datetime
        # start_datetime = pd.to_datetime(start)

        # # Estrai il timestamp iniziale come numero di secondi trascorsi dalla data minima
        # start_timestamp = (start_datetime - combined_df['Timestamp'].min()).total_seconds()

        # Vertical line on start
        plt.axvline(x=start_timestamp, color='r', linestyle='--', label='Start Benchmark')

        plt.xlabel('Time (seconds)')
        plt.ylabel(f'{col} Value')
        # plt.title(f'{workload} Workload Percentiles over Time for {col} (runs: {runs})')
        plt.title(f'{workload} Workload Percentiles over Time for {col}', y=1.15)
        plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.14), ncol=len(percentiles), fontsize='small', title='Percentiles', title_fontsize='medium')
        plt.grid(True, linestyle='--', alpha=0.5, zorder=0)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        if not os.path.exists(f'{directory_path}/img'):
            os.makedirs(f'{directory_path}/img')
        
        plt.savefig(f'{directory_path}/img/{workload}_{col}_plot.png')
        plt.savefig(f'{directory_path}/img/{workload}_{col}_plot.pdf', dpi=300, bbox_inches='tight')
