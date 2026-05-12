import re
import json
import os
import pandas as pd


def region_fix(input_string):
    parts = input_string.split('-')

    directions = {
        's': 'south',
        'n': 'north',
        'e': 'east',
        'w': 'west'
    }

    if len(parts) >= 2:
        parts[1] = ''.join(directions.get(char, char) for char in parts[1])

    output_string = '-'.join(parts)

    return output_string


kollaps_aws_df = pd.read_csv('/tmp/aws.csv')
kollaps_aws_df['k_latency'] = 0.0
kollaps_aws_df['k_throughput'] = 0.0
# results = pd.DataFrame(columns=['src_region', 'dst_region', 'latency', 'throughput'])

directory = '/results/latencies'
# throughput = 0

file_iperf_pattern = re.compile(r"iperf3-client-(.+)-to-(.+)\.json")
for filename in os.listdir(directory):
    match = file_iperf_pattern.match(filename)
    if match:
        file_path = os.path.join(directory, filename)
        
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)

        src_fix_name = match.group(1)
        dst_fix_name = match.group(2)      
        
        src_region = region_fix(src_fix_name)
        dst_region = region_fix(dst_fix_name)

        k_latency = data['end']['streams'][0]['sender']['max_rtt'] / 1000
        k_latency = k_latency / 2
        
        k_throughput = data['end']['sum_sent']['bits_per_second'] / 1000000
        
        row = kollaps_aws_df.loc[(kollaps_aws_df['src_region'] == src_region) & (kollaps_aws_df['dst_region'] == dst_region)]
        if row.empty:
            kollaps_aws_df.loc[(kollaps_aws_df['src_region'] == dst_region) & (kollaps_aws_df['dst_region'] == src_region), 'k_latency'] = k_latency               
            kollaps_aws_df.loc[(kollaps_aws_df['src_region'] == dst_region) & (kollaps_aws_df['dst_region'] == src_region), 'k_throughput'] = k_throughput
        else:            
            kollaps_aws_df.loc[(kollaps_aws_df['src_region'] == src_region) & (kollaps_aws_df['dst_region'] == dst_region), 'k_latency'] = k_latency               
            kollaps_aws_df.loc[(kollaps_aws_df['src_region'] == src_region) & (kollaps_aws_df['dst_region'] == dst_region), 'k_throughput'] = k_throughput


kollaps_aws_df.to_csv('/results/kollaps-df.csv', index=False) 