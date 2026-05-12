import os
import pandas as pd
import json
import re
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed

ping_dir = "misc/cloudping"
regions = ['af-south-1', 'ap-northeast-1', 'ap-south-1', 'ap-southeast-2', 'eu-north-1', 'eu-south-1', 'me-south-1', 'sa-east-1', 'us-east-2', 'us-west-2']
date_pattern = r"cloudping_(\d{8})_(\d{6})\.json"
start_date = datetime.strptime("20230410", "%Y%m%d")
end_date = datetime.strptime("20250114", "%Y%m%d")


def process_file(filename):
    match = re.search(date_pattern, filename)
    if not match:
        return []

    date_string = match.group(1)
    hour_string = match.group(2)
    date = date_string + hour_string
    origin = datetime.strptime(date, "%Y%m%d%H%M%S")

    if not (start_date <= origin <= end_date):
        return []

    file_path = os.path.join(ping_dir, filename)

    try:
        with open(file_path, encoding='utf-8') as json_file:
            json_data = json.load(json_file)
    except UnicodeDecodeError:
        try:
            with open(file_path, encoding='latin1') as json_file:
                json_data = json.load(json_file)
        except Exception:
            return []
    except json.decoder.JSONDecodeError:
        return []

    if "errorType" in json_data:
        return []

    rows = []
    # for data_entry in json_data:
    #     src_region = data_entry["region"]
    #     for average_data in data_entry["averages"]:
    #         dst_region = average_data["regionTo"]
    #         ping_avg = average_data["average"]
    #         rows.append({
    #             'src_region': src_region,
    #             'dst_region': dst_region,
    #             'ping_avg': ping_avg,
    #             'origin': origin
    #         })

    for data_entry in json_data:                    
        src_region = data_entry["region"]
        if src_region in regions:
            averages = data_entry["averages"]
            for average_data in averages:
                dst_region = average_data["regionTo"]                                
                if dst_region in regions and dst_region != src_region:
                    ping_avg = average_data["average"]
                    rows.append({
                        'src_region': src_region,
                        'dst_region': dst_region,
                        'ping_avg': ping_avg,
                        'origin': origin
                    })                    
                    
    return rows


def main():
    all_rows = []

    with ProcessPoolExecutor() as executor:
        futures = [executor.submit(process_file, f) for f in os.listdir(ping_dir)]
        for future in as_completed(futures):
            result = future.result()
            if result:
                all_rows.extend(result)

    df = pd.DataFrame(all_rows)
    df = df.sort_values(by='origin')
    # df.to_csv('misc/ping-complete.csv', index=False)
    df.to_csv('misc/ping.csv', index=False)    
    # print(df)


if __name__ == "__main__":
    main()
