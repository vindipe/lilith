import json
import matplotlib.pyplot as plt
import numpy as np
import sys
import os


t_one = 60
t_one_text = "S1"
t_two = 120
t_two_text = "S2"
t_three = 180
t_three_text = "S3"


if len(sys.argv) != 2:
    print("Usage: python3 script.py <directory_path>")
    sys.exit(1)

directory_path = sys.argv[1]

if "paypal" in directory_path:
    t_one = 600
    t_one_text = "N1"
    t_two = 800
    t_two_text = "N2"
    t_three = 860
    t_three_text = "N3"

cartella_img = os.path.join(directory_path, 'img')

cartella_primary = next((folder for folder in os.listdir(directory_path) if 'primary' in folder), None)
if cartella_primary is None:
    print(f"No primary results found in {directory_path}. Skipping {os.path.basename(__file__)}.")
    sys.exit(0)

cartella_workloads = os.path.join(directory_path, cartella_primary, 'workloads')

for workload in os.listdir(cartella_workloads):
    print(workload)
    cartella_path = os.path.join(cartella_workloads, workload)

    for run in os.listdir(cartella_path):
        sotto_cartella_path = os.path.join(cartella_path, run)

        json_file_path = os.path.join(sotto_cartella_path, 'results.json')
        if os.path.isfile(json_file_path):
            with open(json_file_path, 'r') as f:
                data = json.load(f)

            commit_times = []
            latency_times = []

            for location in data['Locations']:
                for client in location['Clients']:
                    for interaction in client['Interactions']:
                        if interaction['CommitTime'] > 0:
                            commit_times.append(interaction['CommitTime'])
                            latency_times.append(interaction['CommitTime']-interaction['SubmitTime'])

            commit_times = np.array(commit_times)
            commit_times = np.floor(commit_times).astype(int)

            unique, counts = np.unique(commit_times, return_counts=True)
            tps = dict(zip(unique, counts))

            seconds = list(tps.keys())
            commits_per_second = list(tps.values())

            fig, ax = plt.subplots(figsize=(10, 6))

            ax.plot(seconds, commits_per_second, marker='o', linestyle='-', color='b')

            ax.axvline(x=t_one, color='red', linestyle='-', linewidth=7)
            ax.text(t_one, ax.get_ylim()[1], t_one_text, color='black', ha='center', va='bottom', fontsize=20)

            ax.axvline(x=t_two, color='red', linestyle='--', linewidth=7)
            ax.text(t_two, ax.get_ylim()[1], t_two_text, color='black', ha='center', va='bottom', fontsize=20)

            ax.axvline(x=t_three, color='red', linestyle='-.', linewidth=7)
            ax.text(t_three, ax.get_ylim()[1], t_three_text, color='black', ha='center', va='bottom', fontsize=20)

            ax.grid(axis='y', linestyle='--', alpha=0.7)
            ax.set_axisbelow(True)

            ax.set_xlabel('Time', fontsize=24)
            ax.set_ylabel('TPS', fontsize=23)
            # ax.set_title('Transaction Commit per Second (TPS)')

            # ax.set_yticks([0, 200, 400, 600, 800, 1000, 1200, 1400])

            # ax.set_xticks(ax.get_xticks())
            ax.set_xticklabels(ax.get_xticklabels(), fontsize=22)
            # ax.set_yticks(ax.get_yticks())
            ax.set_yticklabels(ax.get_yticklabels(), fontsize=22)

            # ax.set_xlim(left=None, right=None)
            ax.set_ylim(bottom=None, top=None)
            # ax.set_ylim(0, 1600)
            # ax.set_yscale('log')
            # ax.set_ylim(0, 15)  # Set the y-axis limits

            plt.savefig(f'{cartella_img}/{workload}-{run}-tps-json.pdf', bbox_inches='tight')
            plt.savefig(f'{cartella_img}/{workload}-{run}-tps-json.png', dpi=300, bbox_inches='tight')
            plt.close()


            latency_times = np.array(latency_times)
            latency_times.sort()

            cdf = np.arange(1, len(latency_times) + 1) / len(latency_times)

            fig, ax = plt.subplots(figsize=(10, 6))

            ax.plot(latency_times, cdf, marker='o', linestyle='-', color='g')

            ax.grid(axis='y', linestyle='--', alpha=0.7)
            ax.set_axisbelow(True)

            ax.set_xlabel('Latency (sec)', fontsize=24)
            ax.set_ylabel('CDF', fontsize=23)
            # ax.set_title('Transaction Commit per Second (TPS)')

            # ax.set_xticks(ax.get_xticks())
            ax.set_xticklabels(ax.get_xticklabels(), fontsize=22)
            # ax.set_yticks(ax.get_yticks())
            ax.set_yticklabels(ax.get_yticklabels(), fontsize=22)

            plt.savefig(f'{cartella_img}/{workload}-{run}-lat-json.pdf', bbox_inches='tight')
            plt.savefig(f'{cartella_img}/{workload}-{run}-lat-json.png', dpi=300, bbox_inches='tight')
            plt.close()