import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
import sys
import re
import time


def joules_to_kwh(joules):
    # 1 Joule = 2.7778 × 10^-7 kWh
    kwh = joules * 2.7778e-7
    return kwh

if len(sys.argv) != 2:
    print("Usage: python script.py <directory_path>")
    sys.exit(1)

directory_path = sys.argv[1]
energy_folder = os.path.join(directory_path, "energy")

# machines = int(sys.argv[2])

time_frame = 5

intel_rapl_sum = 0
perf_sum = 0
total_time = 0
for file in os.listdir(energy_folder):
    if 'energy' in file:
        file_path = os.path.join(energy_folder, file)
        df = pd.read_csv(file_path)
        
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        first_timestamp = df['Timestamp'].iloc[0]
        last_timestamp = df['Timestamp'].iloc[-1]
        time_difference = (last_timestamp - first_timestamp).total_seconds()
        total_time=(total_time+time_difference)/2

        perf_columns_sum = 0
        for col in df.columns:
            if 'power' in col:
                column_sum = df[col].sum()
                perf_columns_sum += column_sum                
        if perf_sum == 0:
            perf_sum = perf_columns_sum
        else:
            perf_sum = (perf_sum+perf_columns_sum)/2

        first_rapl_energy_microjoules = df.iloc[0]['intel-rapl']
        last_rapl_energy_microjoules = df.iloc[-1]['intel-rapl']
        total_rapl_energy_microjoules = last_rapl_energy_microjoules - first_rapl_energy_microjoules        
        # RAPL energy conversion from microjoules to joules
        total_rapl_energy_joules = total_rapl_energy_microjoules / 1000000     
        if intel_rapl_sum == 0:
            intel_rapl_sum = total_rapl_energy_joules
        else:
            intel_rapl_sum = (intel_rapl_sum+total_rapl_energy_joules)/2

# Converti l'energia totale da joules a kilowattore (kWh)
print(intel_rapl_sum)
# intel_rapl_sum=intel_rapl_sum / time_frame    # W
# intel_rapl_sum=intel_rapl_sum/1000  #kWs
# intel_rapl_sum=intel_rapl_sum/3600  #kWh

intel_rapl_sum=joules_to_kwh(intel_rapl_sum)

print(perf_sum)
perf_sum=joules_to_kwh(perf_sum)
# perf_sum_method1 = perf_sum
# perf_sum_method1=perf_sum_method1/time_frame    # W
# perf_sum_method1=perf_sum_method1/1000  #kWs
# perf_sum_method1=perf_sum_method1/3600  #kWh
# print(perf_sum_method1)

# # print(total_time)
# perf_sum_method2 = perf_sum
# perf_sum_method2=joules_to_kwh(perf_sum_method2)
# print(perf_sum_method2)

# perf_sum_method3 = perf_sum
# perf_sum_method3=perf_sum_method3*2.3/(1e10)*total_time #W
# perf_sum_method3=perf_sum_method3/1000
# print(perf_sum_method3)

# Average cost per kWh (in USD)
average_cost_per_kwh = 0.15

# Total electricity cost
perf_electricity_cost = perf_sum * average_cost_per_kwh
rapl_electricity_cost = intel_rapl_sum * average_cost_per_kwh


print(f"Average energy (kWh) for perf (1 machine) per {int(total_time/60)} minutes execution: {perf_sum}")
print(f"Total (average) electricity cost (USD) for perf (1-machine) per {int(total_time/60)} minutes execution: {perf_electricity_cost}")
# print("Potential cost for a long-running experiment of 2 weeks (USD) for perf:", perf_electricity_cost * 24 * 10)

print("")

print(f"Average energy (kWh) for RAPL (1 machine) per {int(total_time/60)} minutes execution: {intel_rapl_sum}")
print(f"Total (average) electricity cost (USD) for RAPL (1-machine) per {int(total_time/60)} minutes execution: {rapl_electricity_cost}")
# print("Potential cost for a long-running experiment of 2 weeks (USD) for RAPL:", rapl_electricity_cost * 24 * 10)

data = {
    "perf-kWh": [perf_sum],
    "perf-USD": [perf_electricity_cost],
    "RAPL-kWh": [intel_rapl_sum],
    "RAPL-USD": [rapl_electricity_cost]
}


df = pd.DataFrame(data)
df.to_csv(f"{directory_path}/energy_consumption.csv", index=False)