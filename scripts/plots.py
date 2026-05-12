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

# custom_colors = ['#b35806', '#f1a340', '#d8daeb', '#998ec3', '#542788']
# custom_colors = ['#f28e2b', '#fdae61', '#ffffbf', '#abd9e9', '#b39ddb']
custom_colors = ["#d7191c", "#fdae61", "#ffffbf", "#abdda4", "#2b83ba"]

# PERFORMANCE
performances=["tx_ratio", "average_throughput", "average_latency"]

for topology in topologies:
    print(topology)
    topology_df = df[df['mode'] == topology]
    
    refined_topology_df = topology_df[topology_df['dataset'] == '2023']
    refined_topology_df = refined_topology_df[refined_topology_df['link_strategy'] == 'hop']
    # refined_topology_df = refined_topology_df[refined_topology_df['delay'] == 1]
    refined_topology_df = refined_topology_df[refined_topology_df['network_size'] == 1]
    # refined_topology_df = refined_topology_df[refined_topology_df['congestion'] == 0]
    refined_topology_df = refined_topology_df[refined_topology_df['secondaries'] == 10]
    refined_topology_df = refined_topology_df[refined_topology_df['cores'] == 8]
    refined_topology_df = refined_topology_df[refined_topology_df['ram'] == 16]
    refined_topology_df = refined_topology_df[refined_topology_df['dynamic'] == 0]
    
    # grouped_df = workload_df.groupby('hash').agg({
        # 'run': 'max',
    grouped_df = refined_topology_df.groupby(['blockchain', 'workload', 'cores', 'ram', 'secondaries', 'dataset', 'link_strategy', 'network_size', 'dynamic']).agg({
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
    # grouped_df.to_csv(f"grouped_df-{topology}.csv", index=False)  

    fig, axes = plt.subplots(nrows=len(performances), ncols=1, figsize=(23, 11))
    # Flatten axes to iterate over them
    axes = axes.flatten()    
    # axes[row].set_yscale('log')
    
    # order = ['gafam', '10000', 'dota', 'football']
    
    for row, performance in enumerate(performances):
        
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
        sns.barplot(x='workload', y=performance, hue='blockchain', data=grouped_df, legend='brief', ax=axes[row], palette=custom_colors, width=0.7)            
    
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
        bars = bars[:len(bars) - blockchain_number]
        heights = [bar.get_height() for bar in bars]

        # Iterate over the bars and add 'X' label for bars with height 0
        for bar, height in zip(bars, heights):
            if height == 0.0 or height == 0:  
                index = bars.index(bar)  # Get the index of the current bar
                blockchain_name = grouped_df['blockchain'].iloc[index]  # Get the blockchain name from the dataframe                                    
                axes[row].text(bar.get_x() + bar.get_width() / 2, height, f'{blockchain_name}-no-commit', ha='center', va='bottom', fontsize=18, rotation=90)                                
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
        if row == len(performances)-1:
            axes[row].set_xlabel('Workloads', fontsize=26)    
        #     axes[row].set_xticks(axes[row].get_xticks())
        #     axes[row].set_xticklabels(axes[row].get_xticklabels(), fontsize=25)
        else: 
            axes[row].set_xlabel('')
            # axes[row].set_xticklabels('')  
            
        axes[row].set_xticks(axes[row].get_xticks())
        axes[row].set_xticklabels(axes[row].get_xticklabels(), fontsize=25)            
                                
        # plt.xticks(fontsize=14)
        # plt.yticks(fontsize=14)
        if performance == 'average_latency':
            ylabel = 'Block Finality (s)'
            axes[row].set_ylim(0, 200)  # Set the y-axis limits
        elif performance == 'average_throughput':
            ylabel = 'TPS'
            axes[row].set_ylim(0, 1000)  # Set the y-axis limits
        elif performance == 'average_load':            
            ylabel = 'Load (TPS)'
        else:
            ylabel = 'Commit Ratio'
        axes[row].set_ylabel(ylabel, fontsize=25)                        
        axes[row].set_yticks(axes[row].get_yticks())
        axes[row].set_yticklabels(axes[row].get_yticklabels(), fontsize=25)
        
        if performance=='average_load':
            axes[row].set_yscale('log')
        
        axes[row].grid(axis='y', linestyle='--', alpha=0.7)
        axes[row].set_axisbelow(True) 
    
    # plt.suptitle(f'{topology.capitalize()}', fontsize=25, y=1.07)
    
    for ax in axes.flat:
        if ax.get_legend() is not None:
            ax.get_legend().remove()
    
    blockchain_handles, blockchain_labels = axes[0].get_legend_handles_labels()
    # legend = fig.legend(blockchain_handles, blockchain_labels, loc='upper center', bbox_to_anchor=(0.5, 0.97), fancybox=True, shadow=True, ncols=(len(blockchain_labels)), prop={'size': 24})
    
    plt.subplots_adjust(hspace=0.2)
    # plt.subplots_adjust(top=0.2, bottom=0.1, left=0.1, right=0.2, hspace=0.2, wspace=0.5)
    
    plt.tight_layout()  
    # plt.yscale('log')  

    plt.savefig(f'results/plot/performance/{topology}-size1-plot.pdf')
    plt.savefig(f'results/plot/performance/{topology}-size1-plot.png', dpi=300)    
    # plt.savefig(f'results/plot/performance/{topology}-size1-plot.pdf', bbox_extra_artists=(legend,), bbox_inches='tight')
    # plt.savefig(f'results/plot/performance/{topology}-size1-plot.png', dpi=300, bbox_extra_artists=(legend,), bbox_inches='tight')
    plt.close()                    


# OUR DATASET
topology_df = df[df['mode'] == 'full mesh']

refined_topology_df = topology_df[topology_df['workload'] == 'PayPal']
refined_topology_df = refined_topology_df[refined_topology_df['link_strategy'] == 'hop']
# refined_topology_df = refined_topology_df[refined_topology_df['delay'] == 1]
refined_topology_df = refined_topology_df[refined_topology_df['network_size'] == 1]
# refined_topology_df = refined_topology_df[refined_topology_df['congestion'] == 0]
refined_topology_df = refined_topology_df[refined_topology_df['secondaries'] == 10]
refined_topology_df = refined_topology_df[refined_topology_df['cores'] == 8]
refined_topology_df = refined_topology_df[refined_topology_df['ram'] == 16]
refined_topology_df = refined_topology_df[refined_topology_df['dynamic'] == 0]

# grouped_df = workload_df.groupby('hash').agg({
    # 'run': 'max',
grouped_df = refined_topology_df.groupby(['blockchain', 'workload', 'cores', 'ram', 'secondaries', 'dataset', 'link_strategy', 'network_size', 'dynamic']).agg({
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
# grouped_df.to_csv(f"grouped_df-{topology}.csv", index=False)  

fig, axes = plt.subplots(nrows=len(performances), ncols=1, figsize=(8, 11))
# Flatten axes to iterate over them
axes = axes.flatten()    
# axes[row].set_yscale('log')

# order = ['gafam', '10000', 'dota', 'football']
# custom_colors = ['#b35806', '#f1a340', '#d8daeb', '#998ec3', '#542788']

for row, performance in enumerate(performances):
    
    # grouped_df.loc[grouped_df[performance] == 0.0, performance] = 'X'
    # nan_values = grouped_df[grouped_df[performance] == 0.0]
    
    # if performance == 'average_latency':
    #     # Plot both 'average_latency' and 'median_latency' in the same barplot
        
    #     sns.barplot(x='dataset', y='average_latency', hue='blockchain', data=grouped_df, legend='brief', alpha=1, palette=custom_colors)           
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
    sns.barplot(x='dataset', y=performance, hue='blockchain', data=grouped_df, legend='brief', ax=axes[row], palette=custom_colors, width=0.7)            

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
                    
    # Remove the last values from bars
    bars = bars[:len(bars) - blockchain_number]
    heights = [bar.get_height() for bar in bars]

    # Iterate over the bars and add 'X' label for bars with height 0
    for bar, height in zip(bars, heights):
        if height == 0.0 or height == 0:  
            index = bars.index(bar)  # Get the index of the current bar
            blockchain_name = grouped_df['blockchain'].iloc[index]  # Get the blockchain name from the dataframe                                    
            axes[row].text(bar.get_x() + bar.get_width() / 2, height, f'{blockchain_name}-no-commit', ha='center', va='bottom', fontsize=18, rotation=90)                
        elif performance != 'tx_ratio':
            if height > 0 and height < 1:
                axes[row].annotate('1', (bar.get_x() + bar.get_width() / 2., 5), ha='center', va='bottom', fontsize=25, color='black', xytext=(0, 0), textcoords='offset points', rotation=90)                                        
            else:
                axes[row].annotate(f'{int(height)}', (bar.get_x() + bar.get_width() / 2., 5), ha='center', va='bottom', fontsize=25, color='black', xytext=(0, 0), textcoords='offset points', rotation=90)                                        

                    
    # if performance == 'average_latency':
    #     sns.barplot(x='dataset', y='median_latency', hue='blockchain', data=grouped_df, legend='brief', palette='dark:black', alpha=0.9, hatch='//', fill=False, linewidth=1.3)        
                            
    # palette=custom_colors, edgecolor='white', 
    if row == len(performances)-1:
        axes[row].set_xlabel('Network Datasets', fontsize=25)    
    #     axes[row].set_xticks(axes[row].get_xticks())
    #     axes[row].set_xticklabels(axes[row].get_xticklabels(), fontsize=25)
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
        ylabel = 'TPS'
    elif performance == 'average_load':            
        ylabel = 'Load (TPS)'
    else:
        ylabel = 'Commit Ratio'
    axes[row].set_ylabel(ylabel, fontsize=25)                        
    axes[row].set_yticks(axes[row].get_yticks())
    axes[row].set_yticklabels(axes[row].get_yticklabels(), fontsize=25)
    
    if performance=='average_load':
        axes[row].set_yscale('log')
    
    axes[row].grid(axis='y', linestyle='--', alpha=0.7)
    axes[row].set_axisbelow(True) 

# plt.suptitle(f'{topology.capitalize()}', fontsize=25, y=1.07)

for ax in axes.flat:
    if ax.get_legend() is not None:
        ax.get_legend().remove()

blockchain_handles, blockchain_labels = axes[0].get_legend_handles_labels()
# legend = fig.legend(blockchain_handles, blockchain_labels, loc='upper center', bbox_to_anchor=(0.5, 0.97), fancybox=True, shadow=True, ncols=(len(blockchain_labels)), prop={'size': 24})

plt.subplots_adjust(hspace=0.2)
# plt.subplots_adjust(top=0.2, bottom=0.1, left=0.1, right=0.2, hspace=0.2, wspace=0.5)

plt.tight_layout()  
# plt.yscale('log')  

plt.savefig(f'results/plot/performance/full-mesh-our-size1-plot.pdf')
plt.savefig(f'results/plot/performance/full-mesh-our-size1-plot.png', dpi=300)
# plt.savefig(f'results/plot/performance/full-mesh-our-size1-plot.pdf', bbox_extra_artists=(legend,), bbox_inches='tight')
# plt.savefig(f'results/plot/performance/full-mesh-our-size1-plot.png', dpi=300, bbox_extra_artists=(legend,), bbox_inches='tight')
plt.close()    


# WORKLOAD TRENDS -------------------------------------------
topology_df = df[df['mode'] == 'full mesh']

# refined_topology_df = topology_df[topology_df['workload'] == 'PayPal*']
refined_topology_df = topology_df[topology_df['link_strategy'] == 'hop']
# refined_topology_df = refined_topology_df[refined_topology_df['delay'] == 1]
refined_topology_df = refined_topology_df[refined_topology_df['blockchain'] == "Algorand"]
refined_topology_df = refined_topology_df[refined_topology_df['network_size'] == 1]
# refined_topology_df = refined_topology_df[refined_topology_df['congestion'] == 0]
refined_topology_df = refined_topology_df[refined_topology_df['secondaries'] == 10]
refined_topology_df = refined_topology_df[refined_topology_df['cores'] == 8]
refined_topology_df = refined_topology_df[refined_topology_df['ram'] == 16]
refined_topology_df = refined_topology_df[refined_topology_df['dynamic'] == 0]

# grouped_df = workload_df.groupby('hash').agg({
    # 'run': 'max',
grouped_df = refined_topology_df.groupby(['blockchain', 'workload', 'cores', 'ram', 'secondaries', 'dataset', 'link_strategy', 'network_size', 'dynamic']).agg({
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
# grouped_df.to_csv(f"grouped_df-{topology}.csv", index=False)  

fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(13, 4))

sns.barplot(x='workload', y='average_load', hue='blockchain', data=grouped_df, ax=axes, alpha=1)           
                                    
axes.set_xlabel('Workloads', fontsize=25)    
axes.set_xticks(axes.get_xticks())
axes.set_xticklabels(axes.get_xticklabels(), fontsize=25)            
                            
ylabel = 'TPS'    
axes.set_ylabel(ylabel, fontsize=19)                        
axes.set_yticks(axes.get_yticks())
axes.set_yticklabels(axes.get_yticklabels(), fontsize=25)

axes.set_yscale('log')

axes.grid(axis='y', linestyle='--', alpha=0.7)
axes.set_axisbelow(True) 

# if performance != 'tx_ratio':
#     interval = axes.get_yticks()[1] - axes.get_yticks()[0]

#     current_max_height = axes.get_ylim()[1]

#     new_max_height = current_max_height + interval

#     axes.set_ylim(0, new_max_height)

# Get the bars and their heights
bars = axes.patches
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
        axes.text(bar.get_x() + bar.get_width() / 2, height, f'{blockchain_name}-no-commit', ha='center', va='bottom', fontsize=20, rotation=90)                
    elif performance != 'tx_ratio':
        if height > 0 and height < 1:
            axes[row].annotate('1', (bar.get_x() + bar.get_width() / 2., 0.1), ha='center', va='bottom', fontsize=25, color='black', xytext=(0, 0), textcoords='offset points', rotation=90)                                        
        else:
            axes.annotate(f'{int(height)}', (bar.get_x() + bar.get_width() / 2., 0.1), ha='center', va='bottom', fontsize=25, color='black', xytext=(0, 0), textcoords='offset points', rotation=90)                                        
    elif performance == 'tx_ratio':  
        axes[row].annotate(f'{(height*100).round(2)}%', (bar.get_x() + bar.get_width() / 2., 0.1), ha='center', va='bottom', fontsize=25, color='black', xytext=(0, 0), textcoords='offset points', rotation=90)                                        
                

# plt.suptitle(f'{topology.capitalize()}', fontsize=25, y=1.07)

# Remove legends from the plots
axes.get_legend().remove()

plt.tight_layout()

# Save plots
plt.savefig(f'results/plot/average-load-plot.pdf', bbox_inches='tight')
plt.savefig(f'results/plot/average-load-plot.png', dpi=300, bbox_inches='tight')
plt.close()


# INCREASED SIZE
# performances=["tx_ratio", "average_latency"]

# for topology in topologies:
#     print(topology)
#     topology_df = df[df['mode'] == topology]
    
#     refined_topology_df = topology_df[topology_df['dataset'] == '2023']
#     refined_topology_df = refined_topology_df[refined_topology_df['link_strategy'] == 'hop']
#     # refined_topology_df = refined_topology_df[refined_topology_df['delay'] == 1]
#     # refined_topology_df = refined_topology_df[refined_topology_df['network_size'] == 4]
#     # refined_topology_df = refined_topology_df[refined_topology_df['congestion'] == 0]
#     # refined_topology_df = refined_topology_df[refined_topology_df['bandwidth'] == 1]
#     refined_topology_df = refined_topology_df[refined_topology_df['secondaries'] == 10]
#     refined_topology_df = refined_topology_df[refined_topology_df['cores'] == 8]
#     refined_topology_df = refined_topology_df[refined_topology_df['ram'] == 16]
#     refined_topology_df = refined_topology_df[refined_topology_df['dynamic'] == 0]
    
#     # grouped_df = workload_df.groupby('hash').agg({
#         # 'run': 'max',
#     grouped_df = refined_topology_df.groupby(['blockchain', 'workload', 'cores', 'ram', 'secondaries', 'dataset', 'link_strategy', 'network_size', 'dynamic']).agg({
#         'tx_ratio': 'mean',
#         # 'throughput_ratio': 'mean',
#         'latency_ratio': 'mean',
#         # 'commit_number': 'mean',
#         # 'abort_number': 'mean',
#         'average_load': 'mean',
#         'average_throughput': 'mean',
#         'average_latency': 'mean',
#         'median_latency': 'mean',
#         # 'blockchain': 'first',
#         # 'workload': 'first',
#         # 'mode': 'first',
#         # 'dataset': 'first',
#         # 'link_strategy': 'first',
#         # 'delay': 'first',
#         # 'secondaries': 'first',
#         # 'network_size': 'first',
#         # 'congestion': 'first'
#     }).reset_index()        
    
#     # cols_to_remove = ['blockchain', 'workload', 'commit_number', 'abort_number', 'submit_number']
#     # grouped_df.drop(columns=cols_to_remove, inplace=True)      
#     # print(grouped_df)    
#     grouped_df['workloadAndSize'] = grouped_df.apply(lambda row: f"{row['workload']}_{row['network_size']}", axis=1)
#     grouped_df = grouped_df.sort_values(by='workloadAndSize')
#     blockchain_number=df['blockchain'].nunique()
#     # grouped_df.to_csv(f"grouped_df-{topology}.csv", index=False)  

#     fig, axes = plt.subplots(nrows=len(performances), ncols=1, figsize=(30, 9))
#     # Flatten axes to iterate over them
#     axes = axes.flatten()    
#     # axes[row].set_yscale('log')
    
#     # order = ['gafam', '10000', 'dota', 'football']
#     custom_colors = ['#b35806', '#f1a340', '#d8daeb', '#998ec3', '#542788']
    
#     for row, performance in enumerate(performances):
        
#         # grouped_df.loc[grouped_df[performance] == 0.0, performance] = 'X'
#         # nan_values = grouped_df[grouped_df[performance] == 0.0]
        
#         if performance == 'average_latency':
#             # Plot both 'average_latency' and 'median_latency' in the same barplot
            
#             sns.barplot(x='workloadAndSize', y='average_latency', hue='blockchain', data=grouped_df, legend='brief', alpha=1, palette=custom_colors)           
#             # sns.barplot(x='workload', y='median_latency', hue='blockchain', data=grouped_df, legend='brief', palette='dark:black', alpha=0.9, hatch='//', fill=False, linewidth=1.3)
#             # axes[row].errorbar(grouped_df['workload'], grouped_df['average_latency'], yerr=grouped_df['median_latency'])
            
#             # lat_value = 'latency_ratio'
#             # num_hues = len(np.unique(grouped_df['blockchain']))            
#             # for (hue, df_hue), dogde_dist in zip(grouped_df.groupby('blockchain'), np.linspace(-0.4, 0.4, 2 * num_hues + 1)[1::2]):
#             #     bars = axes[row].errorbar(data=df_hue, x='workload', y='average_latency', yerr=lat_value, ls='', lw=3, color='black')
#             #     xys = bars.lines[0].get_xydata()
#             #     bars.remove()
#             # -    axes[row].errorbar(data=df_hue, x=xys[:, 0] + dogde_dist, y='average_latency', yerr=lat_value, ls='', lw=3, color='black')            
#         else:
#             sns.barplot(x='workloadAndSize', y=performance, hue='blockchain', data=grouped_df, legend='brief', ax=axes[row], palette=custom_colors)            
        
#             # Limit y-axis for 'tx_ratio'
#             if performance == 'tx_ratio':
#                 axes[row].set_ylim(0, 1)

#         if performance != 'tx_ratio':
#             interval = axes[row].get_yticks()[1] - axes[row].get_yticks()[0]

#             current_max_height = axes[row].get_ylim()[1]

#             new_max_height = current_max_height + interval

#             axes[row].set_ylim(0, new_max_height)

#         # Get the bars and their heights
#         bars = axes[row].patches
#         # heights = [bar.get_height() for bar in bars]        
#         # print(bars)
#         # print(heights)        
                        
#         # Remove the last values from bars
#         bars = bars[:len(bars) - blockchain_number]
#         heights = [bar.get_height() for bar in bars]

#         # Iterate over the bars and add 'X' label for bars with height 0
        # for bar, height in zip(bars, heights):
        #     if height == 0.0 or height == 0:  
        #         index = bars.index(bar)  # Get the index of the current bar
        #         blockchain_name = grouped_df['blockchain'].iloc[index]  # Get the blockchain name from the dataframe                                    
        #         axes[row].text(bar.get_x() + bar.get_width() / 2, height, f'{blockchain_name}-no-commit', ha='center', va='bottom', fontsize=15, rotation=90)                
#             elif performance != 'tx_ratio':
#                 axes[row].annotate(f'{int(height)}', (bar.get_x() + bar.get_width() / 2., bar.get_height()+1), ha='center', va='bottom', fontsize=13, color='black', xytext=(0, 5), textcoords='offset points', rotation=90)                                        

                        
# #         if performance == 'average_latency':
# #            sns.barplot(x='workloadAndSize', y='median_latency', hue='blockchain', data=grouped_df, legend='brief', palette='dark:black', alpha=0.9, hatch='//', fill=False, linewidth=1.3)        
                                
#         # palette=custom_colors, edgecolor='white', 
#         if row == len(performances)-1:
#             axes[row].set_xlabel('Workloads + Size', fontsize=25)    
#         #     axes[row].set_xticks(axes[row].get_xticks())
#         #     axes[row].set_xticklabels(axes[row].get_xticklabels(), fontsize=25)
#         else: 
#             axes[row].set_xlabel('')
#             # axes[row].set_xticklabels('')  

#         axes[row].set_xticks(axes[row].get_xticks())
#         axes[row].set_xticklabels(axes[row].get_xticklabels(), fontsize=25)                                
                                
#         # plt.xticks(fontsize=14)
#         # plt.yticks(fontsize=14)
#         if performance == 'average_latency':
#             ylabel = 'Block Finality (s)'
#         elif performance == 'average_throughput':
#             ylabel = 'TPS'
#         elif performance == 'average_load':            
#             ylabel = 'Load (TPS)'
#         else:
#             ylabel = 'Commit Ratio'
#         axes[row].set_ylabel(ylabel, fontsize=25)        
#         axes[row].set_yticks(axes[row].get_yticks())
#         axes[row].set_yticklabels(axes[row].get_yticklabels(), fontsize=25)
        
#         if performance=='average_load':
#             axes[row].set_yscale('log')
        
#         axes[row].grid(axis='y', linestyle='--', alpha=0.7)
#         axes[row].set_axisbelow(True) 
    
#     # plt.suptitle(f'{topology.capitalize()}', fontsize=25, y=1.07)
    
#     for ax in axes.flat:
#         if ax.get_legend() is not None:
#             ax.get_legend().remove()
    
#     blockchain_handles, blockchain_labels = axes[0].get_legend_handles_labels()
#     legend = fig.legend(blockchain_handles, blockchain_labels, loc='upper center', bbox_to_anchor=(0.5, 0.95), fancybox=True, shadow=True, ncols=(len(blockchain_labels)), prop={'size': 19})
    
#     # plt.subplots_adjust(bottom=0.8)
#     plt.subplots_adjust(hspace=0.2)
    
#     # plt.tight_layout()  
#     # plt.yscale('log')  
    
#     plt.savefig(f'results/plot/performance/{topology}-incsize-plot.pdf', bbox_extra_artists=(legend,), bbox_inches='tight')
#     plt.savefig(f'results/plot/performance/{topology}-incsize-plot.png', dpi=300, bbox_extra_artists=(legend,), bbox_inches='tight')
#     plt.close()                    
    
    

# PERFORMANCE
# performances=["tx_ratio", "average_throughput", "average_latency"]

for topology in topologies:
    print(topology)
    topology_df = df[df['mode'] == topology]
    
    refined_topology_df = topology_df[topology_df['dataset'] == '2023']
    refined_topology_df = refined_topology_df[refined_topology_df['link_strategy'] == 'hop']
    # refined_topology_df = refined_topology_df[refined_topology_df['delay'] == 1]
    refined_topology_df = refined_topology_df[refined_topology_df['network_size'] == 4]
    # refined_topology_df = refined_topology_df[refined_topology_df['congestion'] == 0]
    refined_topology_df = refined_topology_df[refined_topology_df['secondaries'] == 10]
    refined_topology_df = refined_topology_df[refined_topology_df['cores'] == 8]
    refined_topology_df = refined_topology_df[refined_topology_df['ram'] == 16]
    refined_topology_df = refined_topology_df[refined_topology_df['dynamic'] == 0]
    
    # grouped_df = workload_df.groupby('hash').agg({
        # 'run': 'max',
    grouped_df = refined_topology_df.groupby(['blockchain', 'workload', 'cores', 'ram', 'secondaries', 'dataset', 'link_strategy', 'network_size', 'dynamic']).agg({
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
    # grouped_df.to_csv(f"grouped_df-{topology}.csv", index=False)  

    fig, axes = plt.subplots(nrows=len(performances), ncols=1, figsize=(23, 11))
    # Flatten axes to iterate over them
    axes = axes.flatten()    
    # axes[row].set_yscale('log')
    
    # order = ['gafam', '10000', 'dota', 'football']
    # custom_colors = ['#b35806', '#f1a340', '#d8daeb', '#998ec3', '#542788']
    
    for row, performance in enumerate(performances):
        
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
        sns.barplot(x='workload', y=performance, hue='blockchain', data=grouped_df, legend='brief', ax=axes[row], palette=custom_colors, width=0.7)            
        
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
        bars = bars[:len(bars) - blockchain_number]
        heights = [bar.get_height() for bar in bars]

        # Iterate over the bars and add 'X' label for bars with height 0
        for bar, height in zip(bars, heights):
            if height == 0.0 or height == 0:  
                index = bars.index(bar)  # Get the index of the current bar
                blockchain_name = grouped_df['blockchain'].iloc[index]  # Get the blockchain name from the dataframe                                    
                axes[row].text(bar.get_x() + bar.get_width() / 2, height, f'{blockchain_name}-no-commit', ha='center', va='bottom', fontsize=18, rotation=90)                                
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
        if row == len(performances)-1:
            axes[row].set_xlabel('Workloads', fontsize=26)    
        #     axes[row].set_xticks(axes[row].get_xticks())
        #     axes[row].set_xticklabels(axes[row].get_xticklabels(), fontsize=25)
        else: 
            axes[row].set_xlabel('')
            # axes[row].set_xticklabels('')  
            
        axes[row].set_xticks(axes[row].get_xticks())
        axes[row].set_xticklabels(axes[row].get_xticklabels(), fontsize=25)            
                                
        # plt.xticks(fontsize=14)
        # plt.yticks(fontsize=14)
        if performance == 'average_latency':
            ylabel = 'Block Finality (s)'
            axes[row].set_ylim(0, 200)  # Set the y-axis limits
        elif performance == 'average_throughput':
            ylabel = 'TPS'
            axes[row].set_ylim(0, 1000)  # Set the y-axis limits
        elif performance == 'average_load':            
            ylabel = 'Load (TPS)'
        else:
            ylabel = 'Commit Ratio'
        axes[row].set_ylabel(ylabel, fontsize=25)                        
        axes[row].set_yticks(axes[row].get_yticks())
        axes[row].set_yticklabels(axes[row].get_yticklabels(), fontsize=25)
        
        if performance=='average_load':
            axes[row].set_yscale('log')
        
        axes[row].grid(axis='y', linestyle='--', alpha=0.7)
        axes[row].set_axisbelow(True) 
    
    # plt.suptitle(f'{topology.capitalize()}', fontsize=25, y=1.07)
    
    for ax in axes.flat:
        if ax.get_legend() is not None:
            ax.get_legend().remove()
    
    blockchain_handles, blockchain_labels = axes[0].get_legend_handles_labels()
    # legend = fig.legend(blockchain_handles, blockchain_labels, loc='upper center', bbox_to_anchor=(0.5, 0.97), fancybox=True, shadow=True, ncols=(len(blockchain_labels)), prop={'size': 24})
    
    plt.subplots_adjust(hspace=0.2)
    # plt.subplots_adjust(top=0.2, bottom=0.1, left=0.1, right=0.2, hspace=0.2, wspace=0.5)
    
    plt.tight_layout()  
    # plt.yscale('log')  

    plt.savefig(f'results/plot/performance/{topology}-incsize-plot.pdf')
    plt.savefig(f'results/plot/performance/{topology}-incsize-plot.png', dpi=300)    
    # plt.savefig(f'results/plot/performance/{topology}-incsize-plot.pdf', bbox_extra_artists=(legend,), bbox_inches='tight')
    # plt.savefig(f'results/plot/performance/{topology}-incsize-plot.png', dpi=300, bbox_extra_artists=(legend,), bbox_inches='tight')
    plt.close()     

for size in [1,4]:
    for blockchain in blockchains:
        print(blockchain)                      
        topology_df = df[df['blockchain'] == blockchain]

        refined_topology_df = topology_df[topology_df['dataset'] == '2023']
        refined_topology_df = refined_topology_df[refined_topology_df['link_strategy'] == 'hop']
        # refined_topology_df = refined_topology_df[refined_topology_df['delay'] == 1]
        refined_topology_df = refined_topology_df[refined_topology_df['network_size'] == size]
        # refined_topology_df = refined_topology_df[refined_topology_df['congestion'] == 0]
        refined_topology_df = refined_topology_df[refined_topology_df['secondaries'] == 10]
        refined_topology_df = refined_topology_df[refined_topology_df['cores'] == 8]
        refined_topology_df = refined_topology_df[refined_topology_df['ram'] == 16]
        refined_topology_df = refined_topology_df[refined_topology_df['dynamic'] == 0]
        
        # grouped_df = workload_df.groupby('hash').agg({
            # 'run': 'max',
        grouped_df = refined_topology_df.groupby(['mode', 'blockchain', 'workload', 'cores', 'ram', 'secondaries', 'dataset', 'link_strategy', 'network_size', 'dynamic']).agg({
            'MiB-Tx': 'mean',
            'MiB-Rx': 'mean'
        }).reset_index()   
        
        # grouped_df['MiB-Tx'] = grouped_df['MiB-Tx'].astype(int)
        # grouped_df['MiB-Rx'] = grouped_df['MiB-Rx'].astype(int)
            
        # cols_to_remove = ['blockchain', 'workload', 'commit_number', 'abort_number', 'submit_number']
        # grouped_df.drop(columns=cols_to_remove, inplace=True)      
        # print(grouped_df)    
        # blockchain_number=df['blockchain'].nunique() # 
        # grouped_df.to_csv(f"grouped_df-{topology}.csv", index=False)         
        
        fig, axes = plt.subplots(nrows=len(workloads), ncols=1, figsize=(15, 12))
        # Flatten axes to iterate over them
        axes = axes.flatten()    
        # axes[row].set_yscale('log')
        custom_colors = ['#b35806', '#f1a340']

        for row, workload in enumerate(workloads):  
            tmp_df = grouped_df[grouped_df['workload'] == workload]  
            # print(tmp_df)
            # sns.barplot(x='mode', y='network', hue='verse', data=grouped_df, legend='brief', palette=custom_colors)           
            # y=performance, hue='blockchain'
            sns.barplot(x='mode', y='value', hue='variable', data=pd.melt(tmp_df, id_vars=['mode'], value_vars=['MiB-Tx', 'MiB-Rx']), legend='brief', palette=custom_colors, ax=axes[row], width=0.7)

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
                    axes[row].text(bar.get_x() + bar.get_width() / 2, height, f'{blockchain_name}-no-commit', ha='center', va='bottom', fontsize=18, rotation=90)                                
                elif performance != 'tx_ratio':
                    if height > 0 and height < 1:
                        axes[row].annotate('1', (bar.get_x() + bar.get_width() / 2., 5), ha='center', va='bottom', fontsize=25, color='black', xytext=(0, 0), textcoords='offset points', rotation=90)                                        
                    else:
                        axes[row].annotate(f'{int(height)}', (bar.get_x() + bar.get_width() / 2., 5), ha='center', va='bottom', fontsize=25, color='black', xytext=(0, 0), textcoords='offset points', rotation=90)                                        
                elif performance == 'tx_ratio':  
                    axes[row].annotate(f'{(height*100).round(2)}%', (bar.get_x() + bar.get_width() / 2., 0.02), ha='center', va='bottom', fontsize=25, color='black', xytext=(0, 0), textcoords='offset points', rotation=90)                                        
                            
                                    
            # palette=custom_colors, edgecolor='white', 
            if row == len(workloads)-1:
                axes[row].set_xlabel('Network Topologies', fontsize=25)    
                axes[row].set_xticks(axes[row].get_xticks())
                axes[row].set_xticklabels(axes[row].get_xticklabels(), fontsize=25)
            else: 
                axes[row].set_xlabel('')
                axes[row].set_xticklabels('')  
                                    
            # plt.xticks(fontsize=14)
            # plt.yticks(fontsize=14)
            axes[row].set_ylabel(f'{workload} MB/s', fontsize=25)        
            axes[row].set_yticks(axes[row].get_yticks())
            axes[row].set_yticklabels(axes[row].get_yticklabels(), fontsize=25)        
            
            axes[row].grid(axis='y', linestyle='--', alpha=0.7)
            axes[row].set_axisbelow(True) 
            
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
                            
            # Remove the last values from bars
            bars = bars[:len(bars) - blockchain_number]
            heights = [bar.get_height() for bar in bars]

            # Iterate over the bars and add 'X' label for bars with height 0
            for bar, height in zip(bars, heights):
                if height == 0.0 or height == 0:  
                    index = bars.index(bar)  # Get the index of the current bar
                    blockchain_name = grouped_df['blockchain'].iloc[index]  # Get the blockchain name from the dataframe                                    
                    axes[row].text(bar.get_x() + bar.get_width() / 2, height, f'{blockchain_name}-no-commit', ha='center', va='bottom', fontsize=18, rotation=90)                                
                elif performance != 'tx_ratio':
                    if height > 0 and height < 1:
                        axes[row].annotate('1', (bar.get_x() + bar.get_width() / 2., 5), ha='center', va='bottom', fontsize=25, color='black', xytext=(0, 0), textcoords='offset points', rotation=90)                                        
                    else:
                        axes[row].annotate(f'{int(height)}', (bar.get_x() + bar.get_width() / 2., 5), ha='center', va='bottom', fontsize=25, color='black', xytext=(0, 0), textcoords='offset points', rotation=90)                                        
                elif performance == 'tx_ratio':  
                    axes[row].annotate(f'{(height*100).round(2)}%', (bar.get_x() + bar.get_width() / 2., 0.02), ha='center', va='bottom', fontsize=25, color='black', xytext=(0, 0), textcoords='offset points', rotation=90)                                        
        
        # plt.suptitle(f'{topology.capitalize()}', fontsize=25, y=1.07)
        
        for ax in axes.flat:
            if ax.get_legend() is not None:
                ax.get_legend().remove()
        
        verse_handles, verse_labels = axes[0].get_legend_handles_labels()
        legend = fig.legend(verse_handles, verse_labels, loc='upper center', bbox_to_anchor=(0.5, 0.95), fancybox=True, shadow=True, ncols=(len(verse_labels)), prop={'size': 19})
        
        # plt.subplots_adjust(bottom=0.8)
        plt.subplots_adjust(hspace=0.2)
        
        # plt.tight_layout()  
        # plt.yscale('log')  
        
        plt.savefig(f'results/plot/network/{blockchain}-size{size}-plot.pdf', bbox_extra_artists=(legend,), bbox_inches='tight')
        plt.savefig(f'results/plot/network/{blockchain}-size{size}-plot.png', dpi=300, bbox_extra_artists=(legend,), bbox_inches='tight')
        plt.close()               



    refined_topology_df = df[df['dataset'] == '2023']
    refined_topology_df = refined_topology_df[refined_topology_df['link_strategy'] == 'hop']
    # refined_topology_df = refined_topology_df[refined_topology_df['delay'] == 1]
    refined_topology_df = refined_topology_df[refined_topology_df['network_size'] == size]
    # refined_topology_df = refined_topology_df[refined_topology_df['congestion'] == 0]
    refined_topology_df = refined_topology_df[refined_topology_df['secondaries'] == 10]
    refined_topology_df = refined_topology_df[refined_topology_df['cores'] == 8]
    refined_topology_df = refined_topology_df[refined_topology_df['ram'] == 16]
    refined_topology_df = refined_topology_df[refined_topology_df['dynamic'] == 0]

    # grouped_df = workload_df.groupby('hash').agg({
        # 'run': 'max',
    grouped_df = refined_topology_df.groupby(['blockchain', 'mode', 'workload', 'cores', 'ram', 'secondaries', 'dataset', 'link_strategy', 'network_size', 'dynamic']).agg({
        'MiB-Tx': 'mean',
        # 'MiB-Rx': 'mean'
    }).reset_index()   

    # grouped_df['MiB-Tx'] = grouped_df['MiB-Tx'].astype(int)
    # grouped_df['MiB-Rx'] = grouped_df['MiB-Rx'].astype(int)
        
    # cols_to_remove = ['blockchain', 'workload', 'commit_number', 'abort_number', 'submit_number']
    # grouped_df.drop(columns=cols_to_remove, inplace=True)      
    # print(grouped_df)    
    # blockchain_number=df['blockchain'].nunique() # 
    # grouped_df.to_csv(f"tmp.csv", index=False)         

    fig, axes = plt.subplots(nrows=len(workloads), ncols=1, figsize=(20, 25))
    # Flatten axes to iterate over them
    axes = axes.flatten()    
    # axes[row].set_yscale('log')
    # custom_colors = ['#b35806', '#f1a340', '#d8daeb', '#998ec3', '#542788']
    custom_colors = ["#d7191c", "#fdae61", "#ffffbf", "#abdda4", "#2b83ba"]
    # fig.text(0, 0.5, 'Network Usage (MB/s)', fontsize=26, va='center', rotation='vertical')  

    workloads = ["DDoS", "FIFA", "GAFAM", "Gaming", "PayPal", "VISA"]
    for row, workload in enumerate(workloads):
        tmp_df = grouped_df[grouped_df['workload'] == workload]  
        # print(tmp_df)
        # sns.barplot(x='mode', y='network', hue='verse', data=grouped_df, legend='brief', palette=custom_colors)           
        # y=performance, hue='blockchain'
        sns.barplot(x='mode', y='MiB-Tx', hue='blockchain', data=tmp_df, legend='brief', palette=custom_colors, ax=axes[row], width=0.7)

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
        bars = bars[:len(bars) - blockchain_number]
        heights = [bar.get_height() for bar in bars]

        # Iterate over the bars and add 'X' label for bars with height 0
        for bar, height in zip(bars, heights):
            if height == 0.0 or height == 0:  
                index = bars.index(bar)  # Get the index of the current bar
                blockchain_name = grouped_df['blockchain'].iloc[index]  # Get the blockchain name from the dataframe                                    
                axes[row].text(bar.get_x() + bar.get_width() / 2, height, f'{blockchain_name}-no-commit', ha='center', va='bottom', fontsize=18, rotation=90)                
            elif performance != 'tx_ratio':
                axes[row].annotate(f'{height.round(2)}', (bar.get_x() + bar.get_width() / 2., 0.1), ha='center', va='bottom', fontsize=25, color='black', xytext=(0, 0), textcoords='offset points', rotation=90)                                        

                                
        # palette=custom_colors, edgecolor='white', 
        if row == len(workloads)-1:
            axes[row].set_xlabel('Network Topologies', fontsize=26)    
            axes[row].set_xticks(axes[row].get_xticks())
            axes[row].set_xticklabels(axes[row].get_xticklabels(), fontsize=25)
        else: 
            axes[row].set_xlabel('')
            axes[row].set_xticklabels('')  
                                
        axes[row].set_xlabel('')              
        if size == 1:              
            axes[row].text(0.5, 1.05, f'{workload} - one node per region', transform=axes[row].transAxes, 
               ha='center', va='center', fontsize=26, fontweight='bold') 
        else:
            axes[row].text(0.5, 1.05, f'{workload} - four nodes per region', transform=axes[row].transAxes, 
               ha='center', va='center', fontsize=26, fontweight='bold') 
        
        # axes[row].set_ylabel('MB/s')
        
        # plt.xticks(fontsize=14)
        # plt.yticks(fontsize=14)        
        
        # axes[row].set_yticks(fontsize=23)
        # fig.subplots_adjust(left=0.12)  # Aumenta il margine sinistro
        # axes[row].set_ylabel('') 
        axes[row].set_ylabel(f'Mbps', fontsize=26)        
        # axes[row].set_yticklabels(fontsize=23)        
        axes[row].set_yticks(axes[row].get_yticks())
        axes[row].set_yticklabels(axes[row].get_yticklabels(), fontsize=23)   
        # axes[row].set_yticklabels([int(float(label.get_text())) for label in axes[row].get_yticklabels()], fontsize=23)        
        # axes[row].set_yticklabels(axes[row].get_yticklabels(), fontsize=12)        
        # axes[row].set_yticklabels([print(label) for label in axes[row].get_yticklabels()], fontsize=12)        
        
        axes[row].set_yscale('log')
        axes[row].set_ylim(1e-1, 1e4)  # Set the y-axis limits
        
        axes[row].grid(axis='y', linestyle='--', alpha=0.7)
        axes[row].set_axisbelow(True) 

    # plt.suptitle(f'{topology.capitalize()}', fontsize=25, y=1.07)

    axes[row].set_xlabel('Network Topologies', fontsize=25)    
    for ax in axes.flat:
        if ax.get_legend() is not None:
            ax.get_legend().remove()

    verse_handles, verse_labels = axes[0].get_legend_handles_labels()
    # legend = fig.legend(verse_handles, verse_labels, loc='upper center', bbox_to_anchor=(0.5, 0.92), fancybox=True, shadow=True, ncols=(len(verse_labels)), prop={'size': 24})

    # plt.subplots_adjust(bottom=0.8)
    plt.subplots_adjust(hspace=0.2)
    # plt.subplots_adjust(left=0.1)
    
    plt.tight_layout()  
    # plt.yscale('log')      

    plt.savefig(f'results/plot/network/workloads-size{size}-plot.pdf')
    plt.savefig(f'results/plot/network/workloads-size{size}-plot.png', dpi=300)
    # plt.savefig(f'results/plot/network/workloads-size{size}-plot.pdf', bbox_extra_artists=(legend,), bbox_inches='tight')
    # plt.savefig(f'results/plot/network/workloads-size{size}-plot.png', dpi=300, bbox_extra_artists=(legend,), bbox_inches='tight')
    plt.close()                   