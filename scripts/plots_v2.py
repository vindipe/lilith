# Libraries
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import time
import os
import re
import sys
import hashlib


directory_path='results/new'

df = pd.read_csv(f"{directory_path}/join-bench-results.csv")


df['mode'] = df['mode'].str.rstrip('-l')
df['dataset'] = df['dataset'].replace({'diablo': '2023', 'our': '2024'})
df['workload'] = df['workload'].replace({'dota': 'Gaming', 'football': 'FIFA', 'paypal': 'PayPal', 'visa':'VISA', 'gafam':'Exchange', '10000':'DDoS'})
df['blockchain'] = df['blockchain'].replace({'poa': 'Ethereum', 'diem': 'Diem', 'algorand': 'Algorand', 'solana':'Solana', 'quorum':'Quorum'})

# PLOT
df['tx_ratio'] = df['commit_number'] / df['submit_number']
df['tx_ratio'] = df['tx_ratio'].fillna(0.0)

df['latency_ratio'] = df['average_latency'] / df['median_latency']
df['latency_ratio'] = df['latency_ratio'].fillna(0.0)
df['median_latency'] = df['median_latency'].fillna(0.0)

cols_to_remove = ['commit_number', 'abort_number', 'submit_number']
df.drop(columns=cols_to_remove, inplace=True)       

workloads=df['workload'].unique()
blockchains=df['blockchain'].unique()
topologies = df['mode'].unique()
blockchain_number = df['blockchain'].nunique()
bandwidths = sorted(df['bandwidth'].unique())
switches = sorted(df['switch'].unique())
latencies = sorted(df['latency'].unique())


# PERFORMANCE
performances=["average_throughput", "average_latency"]

for bandwidth in bandwidths:
    for switch in switches:
        
        topology_df = df[df['mode'] == 'scale-free']

        
        refined_topology_df = topology_df[topology_df['workload'] == 'FIFA']
        refined_topology_df = refined_topology_df[refined_topology_df['link_strategy'] == 'hop']
        # refined_topology_df = refined_topology_df[refined_topology_df['delay'] == 1]
        refined_topology_df = refined_topology_df[refined_topology_df['network_size'] == 1]
        # refined_topology_df = refined_topology_df[refined_topology_df['congestion'] == 0]
        refined_topology_df = refined_topology_df[refined_topology_df['secondaries'] == 10]
        refined_topology_df = refined_topology_df[refined_topology_df['cores'] == 8]
        refined_topology_df = refined_topology_df[refined_topology_df['ram'] == 16]
        refined_topology_df = refined_topology_df[refined_topology_df['bandwidth'] == bandwidth]
        refined_topology_df = refined_topology_df[refined_topology_df['switch'] == switch]
        # refined_topology_df = refined_topology_df[refined_topology_df['dynamic'] == 0]

        grouped_df = refined_topology_df.groupby(['blockchain', 'workload', 'bandwidth', 'switch', 'latency', 'cores', 'ram', 'secondaries', 'dataset', 'link_strategy', 'network_size', 'dynamic']).agg({
            'tx_ratio': 'mean',
            # 'throughput_ratio': 'mean',
            'latency_ratio': 'mean',
            # 'commit_number': 'mean',
            # 'abort_number': 'mean',
            'average_load': 'mean',
            'average_throughput': 'mean',
            'average_latency': 'mean',
            'median_latency': 'mean',
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

        # cols_to_remove = ['blockchain', 'workload', 'commit_number', 'abort_number', 'submit_number']
        # grouped_df.drop(columns=cols_to_remove, inplace=True)      
        # print(grouped_df)    
        # grouped_df.to_csv(f"grouped_df.csv", index=False)  

        fig, axes = plt.subplots(nrows=len(performances), ncols=1, figsize=(12, 8))
        # Flatten axes to iterate over them
        axes = axes.flatten()    
        # axes[row].set_yscale('log')

        # order = ['gafam', '10000', 'dota', 'football']
        custom_colors = ['#b35806', '#f1a340', '#d8daeb', '#998ec3', '#542788']

        for row, performance in enumerate(performances):                    
            sns.barplot(x='latency', y=performance, hue='blockchain', data=grouped_df, legend='brief', ax=axes[row], palette=custom_colors, width=0.7)            
        
            # Limit y-axis for 'tx_ratio'
            if performance == 'tx_ratio':
                axes[row].set_ylim(0, 1)
            else:
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
            bars = bars[:len(bars) - blockchain_number]
            heights = [bar.get_height() for bar in bars]

            # Iterate over the bars and add 'X' label for bars with height 0
            for bar, height in zip(bars, heights):
                if height == 0.0 or height == 0:  
                    index = bars.index(bar)  # Get the index of the current bar
                    blockchain_name = grouped_df['blockchain'].iloc[index]  # Get the blockchain name from the dataframe                                    
                    axes[row].text(bar.get_x() + bar.get_width() / 2, height, f'{blockchain_name}-no-commit', ha='center', va='bottom', fontsize=17, rotation=90)                
                # elif height == 9999999999999999:   # not valid in case of tx_ratio insertion
                #     index = bars.index(bar)  # Get the index of the current bar
                #     bar.set_height(0)
                #     blockchain_name = grouped_df['blockchain'].iloc[index]  # Get the blockchain name from the dataframe                                    
                #     axes[row].text(bar.get_x() + bar.get_width() / 2, height, f'{blockchain_name}-fail', ha='center', va='bottom', fontsize=15, rotation=90)                                    
                elif performance != 'tx_ratio':
                    # if height != 9999999999999999 and height != 0.0 and height != 0:
                    axes[row].annotate(f'{height:.1f}' if height >= 0.1 else f'{height:.1f}'.lstrip('0') if height != 0 else '0', 
                                    (bar.get_x() + bar.get_width() / 2., bar.get_height()+1), 
                                    ha='center', va='bottom', fontsize=17, color='black', xytext=(0, 5), 
                                    textcoords='offset points', rotation=90)
                            
            # if performance == 'average_latency':
            #     sns.barplot(x='switch', y='median_latency', hue='blockchain', data=grouped_df, legend='brief', palette='dark:black', alpha=0.9, hatch='//', fill=False, linewidth=1.3)        
                                    
            # palette=custom_colors, edgecolor='white', 
            if row == len(performances)-1:
                axes[row].set_xlabel('Links\' Latencies (ms)', fontsize=24)    
            else: 
                axes[row].set_xlabel('')
                # axes[row].set_xticklabels('')          

            axes[row].set_xticks(axes[row].get_xticks())
            axes[row].set_xticklabels(axes[row].get_xticklabels(), fontsize=22)            
                                    
            # plt.xticks(fontsize=14)
            # plt.yticks(fontsize=14)
            if performance == 'average_latency':
                ylabel = 'Block Finality (s)'
            elif performance == 'average_throughput':
                ylabel = 'Throughput (TPS)'
            # else:
            #     ylabel = 'Commit / Submit'
            axes[row].set_ylabel(ylabel, fontsize=23)                        
            axes[row].set_yticks(axes[row].get_yticks())
            axes[row].set_yticklabels(axes[row].get_yticklabels(), fontsize=22)
            
            axes[row].grid(axis='y', linestyle='--', alpha=0.7)
            axes[row].set_axisbelow(True) 

        # plt.suptitle(f'{topology.capitalize()}', fontsize=18, y=1.07)

        # Remove legend
        for ax in axes.flat:
            if ax.get_legend() is not None:
                ax.get_legend().remove()

        blockchain_handles, blockchain_labels = axes[0].get_legend_handles_labels()
        legend = fig.legend(blockchain_handles, blockchain_labels, loc='upper center', bbox_to_anchor=(0.5, 1.0), fancybox=True, shadow=True, ncols=(len(blockchain_labels)), prop={'size': 24})

        plt.subplots_adjust(hspace=0.2)
        # plt.subplots_adjust(top=0.2, bottom=0.1, left=0.1, right=0.2, hspace=0.2, wspace=0.5)

        # plt.tight_layout()  
        # plt.yscale('log')  

        if bandwidth == 1.0:
            bw = "1"
        elif bandwidth == 0.1:
            bw = "01"

        plt.savefig(f'results/plot/performance/scale-free-switches{switch}-bw{bw}-plot.pdf', bbox_extra_artists=(legend,), bbox_inches='tight')
        plt.savefig(f'results/plot/performance/scale-free-switches{switch}-bw{bw}-plot.png', dpi=300, bbox_extra_artists=(legend,), bbox_inches='tight')
        plt.close()    
        

for switch in switches:
    
    refined_topology_df = df[df['dataset'] == '2023']
    refined_topology_df = refined_topology_df[refined_topology_df['link_strategy'] == 'hop']
    # refined_topology_df = refined_topology_df[refined_topology_df['delay'] == 1]
    refined_topology_df = refined_topology_df[refined_topology_df['network_size'] == 1]
    # refined_topology_df = refined_topology_df[refined_topology_df['congestion'] == 0]
    refined_topology_df = refined_topology_df[refined_topology_df['secondaries'] == 10]
    refined_topology_df = refined_topology_df[refined_topology_df['cores'] == 8]
    refined_topology_df = refined_topology_df[refined_topology_df['ram'] == 16]
    refined_topology_df = refined_topology_df[refined_topology_df['dynamic'] == 0]    
    refined_topology_df = refined_topology_df[refined_topology_df['workload'] == 'FIFA']
    refined_topology_df = refined_topology_df[refined_topology_df['switch'] == switch]

    grouped_df = refined_topology_df.groupby(['blockchain', 'mode', 'workload', 'cores', 'ram', 'bandwidth', 'switch', 'latency', 'secondaries', 'dataset', 'link_strategy', 'network_size', 'dynamic']).agg({
        'MiB-Tx': 'mean',
        # 'MiB-Rx': 'mean'
    }).reset_index()   

    # grouped_df['MiB-Tx'] = grouped_df['MiB-Tx'].astype(int)
    # grouped_df['MiB-Rx'] = grouped_df['MiB-Rx'].astype(int)
        
    # cols_to_remove = ['blockchain', 'workload', 'commit_number', 'abort_number', 'submit_number']
    # grouped_df.drop(columns=cols_to_remove, inplace=True)      
    # print(grouped_df)    
    # blockchain_number=df['blockchain'].nunique() # SOSTITUISCO!!!
    # grouped_df.to_csv(f"tmp.csv", index=False)         

    fig, axes = plt.subplots(nrows=len(latencies), ncols=1, figsize=(20, 25))
    # Flatten axes to iterate over them
    axes = axes.flatten()    
    # axes[row].set_yscale('log')
    custom_colors = ['#b35806', '#f1a340', '#d8daeb', '#998ec3', '#542788']

    for row, latency in enumerate(latencies):  
        tmp_df = grouped_df[grouped_df['latency'] == latency]  
        # print(tmp_df)
        # sns.barplot(x='mode', y='network', hue='verse', data=grouped_df, legend='brief', palette=custom_colors)           
        # y=performance, hue='blockchain'
        sns.barplot(x='bandwidth', y='MiB-Tx', hue='blockchain', data=tmp_df, legend='brief', palette=custom_colors, ax=axes[row])
                                
        # palette=custom_colors, edgecolor='white', 
        if row == len(latencies)-1:
            axes[row].set_xlabel('Bandwidth GB/s', fontsize=25)    
            axes[row].set_xticks(axes[row].get_xticks())
            axes[row].set_xticklabels(axes[row].get_xticklabels(), fontsize=23)
        else: 
            axes[row].set_xlabel('')
            axes[row].set_xticklabels('')  
                                
        axes[row].set_xlabel('')                            
        
        axes[row].set_yscale('log')
        axes[row].set_ylim(0.1, 10)  # Set the y-axis limits
        # axes[row].set_ylabel('MB/s')
        
        # plt.xticks(fontsize=14)
        # plt.yticks(fontsize=14)        
        
        # axes[row].set_yticks(fontsize=23)
        axes[row].set_ylabel(f'Links\' Latencies {latency}', fontsize=25)        
        # axes[row].set_yticklabels(fontsize=23)        
        axes[row].set_yticks(axes[row].get_yticks())
        axes[row].set_yticklabels(axes[row].get_yticklabels(), fontsize=23)   
        # axes[row].set_yticklabels([int(float(label.get_text())) for label in axes[row].get_yticklabels()], fontsize=23)        
        # axes[row].set_yticklabels(axes[row].get_yticklabels(), fontsize=12)        
        # axes[row].set_yticklabels([print(label) for label in axes[row].get_yticklabels()], fontsize=12)        
        
        axes[row].grid(axis='y', linestyle='--', alpha=0.7)
        axes[row].set_axisbelow(True) 

    # plt.suptitle(f'{topology.capitalize()}', fontsize=18, y=1.07)

    # axes[row].set_xlabel('Bandwidth', fontsize=25)    
    for ax in axes.flat:
        if ax.get_legend() is not None:
            ax.get_legend().remove()

    verse_handles, verse_labels = axes[0].get_legend_handles_labels()
    legend = fig.legend(verse_handles, verse_labels, loc='upper center', bbox_to_anchor=(0.5, 0.95), fancybox=True, shadow=True, ncols=(len(verse_labels)), prop={'size': 24})

    # plt.subplots_adjust(bottom=0.8)
    plt.subplots_adjust(hspace=0.2)

    # plt.tight_layout()  
    # plt.yscale('log')  

    plt.savefig(f'results/plot/network/workloads2-size1-switches{switch}-plot.pdf', bbox_extra_artists=(legend,), bbox_inches='tight')
    plt.savefig(f'results/plot/network/workloads2-size1-switches{switch}-plot.png', dpi=300, bbox_extra_artists=(legend,), bbox_inches='tight')
    plt.close()                   