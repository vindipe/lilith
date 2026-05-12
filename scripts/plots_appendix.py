# Libraries
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import time
import os
import re
from math import pi


directory_path='results'

# read the joint file
# df = pd.read_csv(f"results/fake-join-bench-results.csv")
df = pd.read_csv(f"{directory_path}/join-bench-results.csv")

df['mode'] = df['mode'].str.rstrip('-l')
df['mode'] = df['mode'].replace({'fat-tree': 'fat-tree', 'full-mesh': 'full mesh', 'hypercube': 'hypercube', 'scale-free': 'scale-free', 'torus': 'torus'})
df['dataset'] = df['dataset'].replace({'diablo': '2023', 'our': '2024'})
df['workload'] = df['workload'].replace({'dota': 'Gaming', 'football': 'FIFA', 'paypal': 'PayPal', 'visa':'VISA', 'gafam':'GAFAM', '10000':'DDoS'})
df['blockchain'] = df['blockchain'].replace({'poa': 'Ethereum', 'diem': 'Diem', 'algorand': 'Algorand', 'solana':'Solana', 'quorum':'Quorum'})

df['network_size'] = df['network_size'].replace({1: '10 nodes', 4: '40 nodes'})

df['tx_ratio'] = df['commit_number'] / df['submit_number']
df['tx_ratio'] = df['tx_ratio'].fillna(0.0)

# df['throughput_ratio'] = df['average_throughput'] / df['average_load']

df['latency_ratio'] = df['average_latency'] / df['median_latency']
df['latency_ratio'] = df['latency_ratio'].fillna(0.0)
df['median_latency'] = df['median_latency'].fillna(0.0)

# cols_to_remove = ['commit_number', 'abort_number', 'submit_number']
# df.drop(columns=cols_to_remove, inplace=True)       

workloads=df['workload'].unique()
blockchains=df['blockchain'].unique()
topologies = df['mode'].unique()
blockchain_number=df['blockchain'].nunique()

workloads = ["DDoS", "FIFA", "GAFAM", "Gaming", "PayPal", "VISA"]

# custom_colors = ['#b35806', '#f1a340', '#d8daeb', '#998ec3', '#542788']
# custom_colors = ['#f28e2b', '#ffbc79', '#d4e157', '#86c7f3', '#b39ddb']
custom_colors = ['#f1a340', '#d8daeb']

# PERFORMANCE
performances=["tx_ratio", "average_throughput", "average_latency"]

for performance in performances:
    print(performance)
    
    for blockchain in blockchains:
        blockchain_df = df[df['blockchain'] == blockchain]
        
        refined_topology_df = blockchain_df[blockchain_df['dataset'] == '2023']
        refined_topology_df = refined_topology_df[refined_topology_df['link_strategy'] == 'hop']
        # refined_topology_df = refined_topology_df[refined_topology_df['delay'] == 1]
        # refined_topology_df = refined_topology_df[refined_topology_df['network_size'] == 1]
        # refined_topology_df = refined_topology_df[refined_topology_df['congestion'] == 0]
        refined_topology_df = refined_topology_df[refined_topology_df['secondaries'] == 10]
        refined_topology_df = refined_topology_df[refined_topology_df['cores'] == 8]
        refined_topology_df = refined_topology_df[refined_topology_df['ram'] == 16]
        refined_topology_df = refined_topology_df[refined_topology_df['dynamic'] == 0]
        
        # grouped_df = workload_df.groupby('hash').agg({
            # 'run': 'max',
        grouped_df = refined_topology_df.groupby(['mode', 'workload', 'cores', 'ram', 'secondaries', 'dataset', 'link_strategy', 'network_size', 'dynamic']).agg({
            performance: 'mean',
            # 'blockchain': 'first',
            # 'workload': 'first',
            # 'mode': 'first',
            # 'dataset': 'first',
            # 'link_strategy': 'first',
            # 'delay': 'first',
            # 'secondaries': 'first',
            # 'network_size': 'first',
            # 'congestion': 'first'
        }).reset_index()        
        

        if performance == 'average_throughput':
            for idx, row in grouped_df.iterrows():
                # if row['blockchain'] == 'Solana' and row['workload'] in ['VISA', 'PayPal']:
                #     continue
                
                # if row['commit_number'] == 0:
                #     grouped_df.loc[idx, 'percentage_difference'] = None
                #     continue
                
                if row['network_size'] == '10 nodes':
                    expected_throughput = row[performance] * 4
                    
                    condition = (grouped_df['mode'] == row['mode']) & \
                                (grouped_df['workload'] == row['workload']) & \
                                (grouped_df['cores'] == row['cores']) & \
                                (grouped_df['ram'] == row['ram']) & \
                                (grouped_df['secondaries'] == row['secondaries']) & \
                                (grouped_df['dataset'] == row['dataset']) & \
                                (grouped_df['link_strategy'] == row['link_strategy']) & \
                                (grouped_df['dynamic'] == row['dynamic']) & \
                                (grouped_df['network_size'] == '40 nodes')  

                    row2 = grouped_df[condition]

                    if not row2.empty:
                        # percentage_diff = ((row2['avg_node_energy'].iloc[0] - expected_energy) / expected_energy) * 100
                        # percentage_diff = (row2['avg_node_energy'].iloc[0] - expected_energy)
                        percentage_diff = expected_throughput
                        
                        grouped_df.loc[row2.index, 'percentage_difference'] = percentage_diff
                    else:
                        print(f"no correspondence row {idx} with network_size == 4")
                    
                    # time.sleep(1)

            grouped_df.loc[grouped_df["network_size"] == '10 nodes', "percentage_difference"] = None        

        
        
        # cols_to_remove = ['blockchain', 'workload', 'commit_number', 'abort_number', 'submit_number']
        # grouped_df.drop(columns=cols_to_remove, inplace=True)      
        # print(grouped_df)    
        # grouped_df.to_csv(f"grouped_df-{topology}.csv", index=False)  

        # fig, axes = plt.subplots(nrows=len(workloads), ncols=1, figsize=(13, 13))
        # if performance == 'average_throughput':
        #     fig, axes = plt.subplots(nrows=len(workloads), ncols=1, figsize=(13, 13.3))
            
        fig, axes = plt.subplots(nrows=len(workloads), ncols=1, figsize=(13, 13))
        # Flatten axes to iterate over them
        axes = axes.flatten()    
        # axes[row].set_yscale('log')
        
        # order = ['gafam', '10000', 'dota', 'football']
        
        for row, workload in enumerate(workloads):
                
            tmp_df = grouped_df[grouped_df['workload'] == workload]
            
            # grouped_df.loc[grouped_df[performance] == 0.0, performance] = 'X'
            # nan_values = grouped_df[grouped_df[performance] == 0.0]
            
            # if performance == 'average_latency':
            #     # Plot both 'average_latency' and 'median_latency' in the same barplot
                
            #     sns.barplot(x='workload', y='average_latency', hue='blockchain', data=grouped_df, legend='brief', alpha=1, palette=custom_colors)           
            #     # sns.barplot(x='workload', y='median_latency', hue='blockchain', data=grouped_df, legend='brief', palette='dark:black', alpha=0.9, hatch='//', fill=False, linewidth=1.3)
            #     # axes[row].errorbar(grouped_df['workload'], grouped_df['average_latency'], yerr=grouped_df['median_latency'])
                
            #     # lat_value = 'latency_ratio'
            #     # num_hues = len(np.unique(grouped_df['blockchain']))            
            #     # for (hue, df_hue), dogde_dist in zip(grouped_df.groupby('blockchain'), np.linspace(-0.4, 0.4, 2 * num_hues + 1)[1::2]):
            #     #     bars = axes[row].errorbar(data=df_hue, x='workload', y='average_latency', yerr=lat_value, ls='', lw=3, color='black')
            #     #     xys = bars.lines[0].get_xydata()
            #     #     bars.remove()
            #     # -    axes[row].errorbar(data=df_hue, x=xys[:, 0] + dogde_dist, y='average_latency', yerr=lat_value, ls='', lw=3, color='black')            
            # else:
            # if performance == 'average_throughput':
            #     sns.lineplot(x='mode', y='percentage_difference', data=tmp_df, ax=axes[row], color='grey', linestyle='dashed', marker='x', linewidth = 2.5, label='average 10 · 40', markersize=22, markeredgecolor='black', markeredgewidth=4)
                
            sns.barplot(x='mode', y=performance, hue='network_size', data=tmp_df, legend='brief', ax=axes[row], palette=custom_colors, width=0.7)            
        
            # Limit y-axis for 'tx_ratio'
            if performance == 'tx_ratio':
                axes[row].set_ylim(0, 1)
            
            if performance != 'tx_ratio':
                interval = axes[row].get_yticks()[1] - axes[row].get_yticks()[0]

                current_max_height = axes[row].get_ylim()[1]

                new_max_height = current_max_height + interval

                axes[row].set_ylim(0, new_max_height)

            # Get the bars and their heights
            bars = axes[row].patches
            # heights = [bar.get_height() for bar in bars]        
            # print(bars)
            # print(heights)
            # print(axes[row].get_legend_handles_labels()[1])        
                            
            # Remove the last values from bars
            bars = bars[:len(bars) - df['network_size'].nunique()]
            heights = [bar.get_height() for bar in bars]

            # Iterate over the bars and add 'X' label for bars with height 0
            for bar, height in zip(bars, heights):
                if height == 0.0 or height == 0:  
                    index = bars.index(bar)  # Get the index of the current bar
                    # blockchain_name = tmp_df['blockchain'].iloc[index]  # Get the blockchain name from the dataframe                                    
                    axes[row].text(bar.get_x() + bar.get_width() / 2, height, 'no-commit', ha='center', va='bottom', fontsize=18, rotation=90)                                
                elif performance != 'tx_ratio':
                    if height > 0 and height < 1:
                        axes[row].annotate('1', (bar.get_x() + bar.get_width() / 2., 5), ha='center', va='bottom', fontsize=25, color='black', xytext=(0, 0), textcoords='offset points', rotation=90)                                        
                    else:
                        axes[row].annotate(f'{int(height)}', (bar.get_x() + bar.get_width() / 2., 5), ha='center', va='bottom', fontsize=25, color='black', xytext=(0, 0), textcoords='offset points', rotation=90)                                        
                elif performance == 'tx_ratio':  
                    axes[row].annotate(f'{(height*100).round(2)}%', (bar.get_x() + bar.get_width() / 2., 0.02), ha='center', va='bottom', fontsize=25, color='black', xytext=(0, 0), textcoords='offset points', rotation=90)                                        
                            
            # if performance == 'average_latency':
            #     sns.barplot(x='workload', y='median_latency', hue='blockchain', data=grouped_df, legend='brief', palette='dark:black', alpha=0.9, hatch='//', fill=False, linewidth=1.3)        
                                    
            # palette=custom_colors, edgecolor='white', 
            if row == len(workloads)-1:
                # axes[row].set_xlabel('Network Topologies', fontsize=26)    
                axes[row].set_xlabel('')    
            #     axes[row].set_xticks(axes[row].get_xticks())
            #     axes[row].set_xticklabels(axes[row].get_xticklabels(), fontsize=25)
                axes[row].set_xticks(axes[row].get_xticks())
                axes[row].set_xticklabels(axes[row].get_xticklabels(), fontsize=25)                      
            else: 
                axes[row].set_xlabel('')
                axes[row].set_xticklabels('')                    
                                    
            # plt.xticks(fontsize=14)
            # plt.yticks(fontsize=14)
            if performance == 'average_latency':
                ylabel = 'Seconds'
                axes[row].text(0.5, 1.05, f'{workload} - Block Finality', transform=axes[row].transAxes, 
                    ha='center', va='center', fontsize=20, fontweight='bold')                  
                axes[row].set_ylim(0, 200)  # Set the y-axis limits
            elif performance == 'average_throughput':
                ylabel = f'TPS'
                axes[row].text(0.5, 1.05, f'{workload} - TPS', transform=axes[row].transAxes, 
                    ha='center', va='center', fontsize=20, fontweight='bold') 
                axes[row].set_ylim(0, 1000)  # Set the y-axis limits
            elif performance == 'tx_ratio':            
                ylabel = f'%'
                axes[row].text(0.5, 1.05, f'{workload} - Commit Ratio', transform=axes[row].transAxes, 
                    ha='center', va='center', fontsize=20, fontweight='bold')                 
            # else:
            #     ylabel = 'Commit Ratio'
            axes[row].set_ylabel(ylabel, fontsize=22)   
            
            # axes[row].text(0.5, 1.05, f'{workload}', transform=axes[row].transAxes, 
            #     ha='center', va='center', fontsize=20, fontweight='bold')   
            # yticks = np.linspace(axes[row].get_ylim()[0], axes[row].get_ylim()[1], 4)
            # axes[row].set_yticks(yticks)                     
            axes[row].set_yticks(axes[row].get_yticks())
            axes[row].set_yticklabels(axes[row].get_yticklabels(), fontsize=20)
            
            if performance=='average_load':
                axes[row].set_yscale('log')
            
            axes[row].grid(axis='y', linestyle='--', alpha=0.7)
            axes[row].set_axisbelow(True) 
        
        # plt.suptitle(f'{topology.capitalize()}', fontsize=25, y=1.07)
        
        for ax in axes.flat:
            if ax.get_legend() is not None:
                ax.get_legend().remove()
        
        # verse_handles, verse_labels = axes[0].get_legend_handles_labels()
        # if performance == 'average_throughput':
        #     desired_order = ['10 nodes', 'average 10 · 40', '40 nodes']
            
        #     order_indices = [verse_labels.index(label) for label in desired_order]

        #     verse_handles = [verse_handles[i] for i in order_indices]
        #     verse_labels = [verse_labels[i] for i in order_indices]      
        # legend = fig.legend(verse_handles, verse_labels, loc='upper center', bbox_to_anchor=(0.5, 0.97), fancybox=True, shadow=True, ncols=(len(verse_labels)), prop={'size': 24})
        
        plt.subplots_adjust(hspace=0.2)
        # plt.subplots_adjust(top=0.2, bottom=0.1, left=0.1, right=0.2, hspace=0.2, wspace=0.5)
        
        # plt.tight_layout()  
        # plt.yscale('log')  
        
        plt.savefig(f'results/plot/performance/{blockchain}-{performance}-size1-plot.pdf', bbox_inches='tight')
        plt.savefig(f'results/plot/performance/{blockchain}-{performance}-size1-plot.png', dpi=300, bbox_inches='tight')
        # plt.savefig(f'results/plot/performance/{blockchain}-{performance}-size1-plot.pdf', bbox_extra_artists=(legend,), bbox_inches='tight')
        # plt.savefig(f'results/plot/performance/{blockchain}-{performance}-size1-plot.png', dpi=300, bbox_extra_artists=(legend,), bbox_inches='tight')        
        plt.close()                    
                

for blockchain in blockchains:
    blockchain_df = df[df['blockchain'] == blockchain]

    refined_topology_df = blockchain_df[blockchain_df['dataset'] == '2023']
    refined_topology_df = refined_topology_df[refined_topology_df['link_strategy'] == 'hop']
    # refined_topology_df = refined_topology_df[refined_topology_df['delay'] == 1]
    # refined_topology_df = refined_topology_df[refined_topology_df['network_size'] == size]
    # refined_topology_df = refined_topology_df[refined_topology_df['congestion'] == 0]
    refined_topology_df = refined_topology_df[refined_topology_df['secondaries'] == 10]
    refined_topology_df = refined_topology_df[refined_topology_df['cores'] == 8]
    refined_topology_df = refined_topology_df[refined_topology_df['ram'] == 16]
    refined_topology_df = refined_topology_df[refined_topology_df['dynamic'] == 0]

    # grouped_df = workload_df.groupby('hash').agg({
        # 'run': 'max',
    grouped_df = refined_topology_df.groupby(['mode', 'workload', 'cores', 'ram', 'secondaries', 'dataset', 'link_strategy', 'network_size', 'dynamic']).agg({
        'MiB-Tx': 'mean',
        # 'MiB-Rx': 'mean'
    }).reset_index()   
    

    for idx, row in grouped_df.iterrows():
        # if row['blockchain'] == 'Solana' and row['workload'] in ['VISA', 'PayPal']:
        #     continue
        
        # if row['commit_number'] == 0:
        #     grouped_df.loc[idx, 'percentage_difference'] = None
        #     continue
        
        if row['network_size'] == '10 nodes':
            expected_throughput = row['MiB-Tx'] * 4
            
            condition = (grouped_df['mode'] == row['mode']) & \
                        (grouped_df['workload'] == row['workload']) & \
                        (grouped_df['cores'] == row['cores']) & \
                        (grouped_df['ram'] == row['ram']) & \
                        (grouped_df['secondaries'] == row['secondaries']) & \
                        (grouped_df['dataset'] == row['dataset']) & \
                        (grouped_df['link_strategy'] == row['link_strategy']) & \
                        (grouped_df['dynamic'] == row['dynamic']) & \
                        (grouped_df['network_size'] == '40 nodes')  

            row2 = grouped_df[condition]

            if not row2.empty:
                # percentage_diff = ((row2['avg_node_energy'].iloc[0] - expected_energy) / expected_energy) * 100
                # percentage_diff = (row2['avg_node_energy'].iloc[0] - expected_energy)
                percentage_diff = expected_throughput
                
                grouped_df.loc[row2.index, 'percentage_difference'] = percentage_diff
            else:
                print(f"no correspondence row {idx} with network_size == 4")
            
            # time.sleep(1)

    grouped_df.loc[grouped_df["network_size"] == '10 nodes', "percentage_difference"] = None        

    # grouped_df['MiB-Tx'] = grouped_df['MiB-Tx'].astype(int)
    # grouped_df['MiB-Rx'] = grouped_df['MiB-Rx'].astype(int)
        
    # cols_to_remove = ['blockchain', 'workload', 'commit_number', 'abort_number', 'submit_number']
    # grouped_df.drop(columns=cols_to_remove, inplace=True)      
    # print(grouped_df)    
    # blockchain_number=df['blockchain'].nunique() 
    # grouped_df.to_csv(f"tmp.csv", index=False)         

    fig, axes = plt.subplots(nrows=len(workloads), ncols=1, figsize=(13, 13))
    # Flatten axes to iterate over them
    axes = axes.flatten()    
    # axes[row].set_yscale('log')
    # custom_colors = ['#b35806', '#f1a340', '#d8daeb', '#998ec3', '#542788']
    # custom_colors = ['#f28e2b', '#ffbc79', '#d4e157', '#86c7f3', '#b39ddb']

    for row, workload in enumerate(workloads):  
        tmp_df = grouped_df[grouped_df['workload'] == workload]  
        # print(tmp_df)
        # sns.barplot(x='mode', y='network', hue='verse', data=grouped_df, legend='brief', palette=custom_colors)           
        # y=performance, hue='blockchain'
        sns.lineplot(x='mode', y='percentage_difference', data=tmp_df, ax=axes[row], color='grey', linestyle='dashed', marker='x', linewidth = 2.5, label='average 10 · 40', markersize=26, markeredgecolor='black', markeredgewidth=5)
        sns.barplot(x='mode', y='MiB-Tx', hue='network_size', data=tmp_df, legend='brief', palette=custom_colors, ax=axes[row], width=0.7)

        # interval = axes[row].get_yticks()[1] - axes[row].get_yticks()[0]

        # current_max_height = axes[row].get_ylim()[1]

        # new_max_height = current_max_height + (interval * 20)

        # axes[row].set_ylim(0, new_max_height)

        # Get the bars and their heights
        bars = axes[row].patches
        # heights = [bar.get_height() for bar in bars]        
        # print(bars)
        # print(heights)        
                        
        # Remove the last values from bars
        bars = bars[:len(bars) - df['network_size'].nunique()]
        heights = [bar.get_height() for bar in bars]

        # Iterate over the bars and add 'X' label for bars with height 0
        for bar, height in zip(bars, heights):
            if height == 0.0 or height == 0:  
                index = bars.index(bar)  # Get the index of the current bar
                # blockchain_name = grouped_df['blockchain'].iloc[index]  # Get the blockchain name from the dataframe                                    
                axes[row].text(bar.get_x() + bar.get_width() / 2, height, f'no-commit', ha='center', va='bottom', fontsize=18, rotation=90)                
            elif performance != 'tx_ratio':
                axes[row].annotate(f'{height.round(2)}', (bar.get_x() + bar.get_width() / 2., 0.01), ha='center', va='bottom', fontsize=25, color='black', xytext=(0, 0), textcoords='offset points', rotation=90)                                        

                                
        # palette=custom_colors, edgecolor='white', 
        if row == len(workloads)-1:
            # axes[row].set_xlabel('Network Topologies', fontsize=26)    
            axes[row].set_xlabel('')    
            axes[row].set_xticks(axes[row].get_xticks())
            axes[row].set_xticklabels(axes[row].get_xticklabels(), fontsize=25)
        else: 
            axes[row].set_xlabel('')
            axes[row].set_xticklabels('')  
                                
        axes[row].set_xlabel('')          
                
        axes[row].set_yscale('log')
        axes[row].set_ylim(1e-1, 1e2)  # Set the y-axis limits
        # axes[row].set_ylim(0.1, 15)  # Set the y-axis limits        
        
        axes[row].text(0.5, 1.05, f'{workload} - Network Load', transform=axes[row].transAxes, 
            ha='center', va='center', fontsize=20, fontweight='bold')         
        
        # axes[row].set_ylabel('MB/s')
        
        # plt.xticks(fontsize=14)
        # plt.yticks(fontsize=14)        
        
        # axes[row].set_yticks(fontsize=23)
        axes[row].set_ylabel(f'Mbps', fontsize=22)        
        # axes[row].set_yticklabels(fontsize=23)                
        # yticks = np.linspace(axes[row].get_ylim()[0], axes[row].get_ylim()[1], 4)
        # axes[row].set_yticks(yticks)                  
        axes[row].set_yticks(axes[row].get_yticks()) 
        axes[row].set_yticklabels(axes[row].get_yticklabels(), fontsize=20)   
        # axes[row].set_yticklabels([int(float(label.get_text())) for label in axes[row].get_yticklabels()], fontsize=23)        
        # axes[row].set_yticklabels(axes[row].get_yticklabels(), fontsize=12)        
        # axes[row].set_yticklabels([print(label) for label in axes[row].get_yticklabels()], fontsize=12)        
        
        axes[row].grid(axis='y', linestyle='--', alpha=0.7)
        axes[row].set_axisbelow(True) 

    # plt.suptitle(f'{topology.capitalize()}', fontsize=25, y=1.07)

    # axes[row].set_xlabel('Network Topologies', fontsize=25)    
    for ax in axes.flat:
        if ax.get_legend() is not None:
            ax.get_legend().remove()

    # verse_handles, verse_labels = axes[0].get_legend_handles_labels()
    # desired_order = ['10 nodes', 'average 10 · 40', '40 nodes']
    
    # order_indices = [verse_labels.index(label) for label in desired_order]

    # verse_handles = [verse_handles[i] for i in order_indices]
    # verse_labels = [verse_labels[i] for i in order_indices]      
    # legend = fig.legend(verse_handles, verse_labels, loc='upper center', bbox_to_anchor=(0.5, 0.92), fancybox=True, shadow=True, ncols=(len(verse_labels)), prop={'size': 24})

    # plt.subplots_adjust(bottom=0.8)
    plt.subplots_adjust(hspace=0.2)

    # plt.tight_layout()  
    # plt.yscale('log')  

    plt.savefig(f'results/plot/network/{blockchain}-workloads-plot.pdf', bbox_inches='tight')
    plt.savefig(f'results/plot/network/{blockchain}-workloads-plot.png', dpi=300, bbox_inches='tight')
    # plt.savefig(f'results/plot/network/{blockchain}-workloads-plot.pdf', bbox_extra_artists=(legend,), bbox_inches='tight')
    # plt.savefig(f'results/plot/network/{blockchain}-workloads-plot.png', dpi=300, bbox_extra_artists=(legend,), bbox_inches='tight')
    plt.close()                           