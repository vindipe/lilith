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


results_path = "results/dynamic"
dynamics = ["packet-drop", "bw-congestion", "node-crash"]

for folder in dynamics:                    
    path = f"{results_path}/{folder}"

    if os.path.exists(path):        
                    
        df = pd.read_csv(f"{path}/dynamics-bench-results.csv")


        df['mode'] = df['mode'].str.rstrip('-l')
        df['dataset'] = df['dataset'].replace({'diablo': '2023', 'our': '2024'})
        df['workload'] = df['workload'].replace({'dota': 'Gaming', 'football': 'FIFA', 'paypal': 'PayPal', 'visa':'VISA', 'gafam':'Exchange', '10000':'DDoS'})
        df['blockchain'] = df['blockchain'].replace({'poa': 'Ethereum', 'diem': 'Diem', 'algorand': 'Algorand', 'solana':'Solana', 'quorum':'Quorum'})

        # PLOT
        df['tx_ratio'] = df['commit_number'] / df['submit_number']
        df['tx_ratio'] = df['tx_ratio'].fillna(0.0)

        # df['throughput_ratio'] = df['average_throughput'] / df['average_load']

        df['latency_ratio'] = df['average_latency'] / df['median_latency']
        df['latency_ratio'] = df['latency_ratio'].fillna(0.0)
        df['median_latency'] = df['median_latency'].fillna(0.0)

        cols_to_remove = ['commit_number', 'abort_number', 'submit_number']
        df.drop(columns=cols_to_remove, inplace=True)       

        workloads=df['workload'].unique()
        blockchains=df['blockchain'].unique()
        topologies = df['mode'].unique()
        blockchain_number=df['blockchain'].nunique()


        # PERFORMANCE
        performances=["tx_ratio", "average_throughput", "average_latency"]


        # DYNAMICS - packet drop --------------------------------------------------
        topology_df = df[df['mode'] == 'full-mesh']

        refined_topology_df = topology_df[topology_df['workload'] == 'PayPal']
        refined_topology_df = refined_topology_df[refined_topology_df['link_strategy'] == 'hop']
        # refined_topology_df = refined_topology_df[refined_topology_df['delay'] == 1]
        refined_topology_df = refined_topology_df[refined_topology_df['network_size'] == 1]
        # refined_topology_df = refined_topology_df[refined_topology_df['congestion'] == 0]
        refined_topology_df = refined_topology_df[refined_topology_df['secondaries'] == 10]
        refined_topology_df = refined_topology_df[refined_topology_df['cores'] == 8]
        refined_topology_df = refined_topology_df[refined_topology_df['ram'] == 16]
        # refined_topology_df = refined_topology_df[refined_topology_df['dynamic'] == 0]

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
        # grouped_df.to_csv(f"grouped_df.csv", index=False)  

        fig, axes = plt.subplots(nrows=len(performances), ncols=1, figsize=(16, 11))
        # Flatten axes to iterate over them
        axes = axes.flatten()    
        # axes[row].set_yscale('log')

        # order = ['gafam', '10000', 'dota', 'football']
        custom_colors = ["#d7191c", "#fdae61", "#ffffbf", "#abdda4", "#2b83ba"]

        for row, performance in enumerate(performances):
            
            # grouped_df.loc[grouped_df[performance] == 0.0, performance] = 'X'
            # nan_values = grouped_df[grouped_df[performance] == 0.0]
            
            # if performance == 'average_latency':
            #     # Plot both 'average_latency' and 'median_latency' in the same barplot
                
            #     sns.barplot(x='dynamic', y='average_latency', hue='blockchain', data=grouped_df, legend='brief', alpha=1, palette=custom_colors)           
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
            sns.barplot(x='dynamic', y=performance, hue='blockchain', data=grouped_df, legend='brief', ax=axes[row], palette=custom_colors, width=0.7)            

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
                    axes[row].text(bar.get_x() + bar.get_width() / 2, height, f'{blockchain_name}-no-commit', ha='center', va='bottom', fontsize=20, rotation=90)                
                elif performance != 'tx_ratio':
                    if height > 0 and height < 1:
                        axes[row].annotate('1', (bar.get_x() + bar.get_width() / 2., 5), ha='center', va='bottom', fontsize=25, color='black', xytext=(0, 0), textcoords='offset points', rotation=90)                                        
                    else:
                        axes[row].annotate(f'{int(height)}', (bar.get_x() + bar.get_width() / 2., 5), ha='center', va='bottom', fontsize=25, color='black', xytext=(0, 0), textcoords='offset points', rotation=90)                                        
                elif performance == 'tx_ratio':  
                    axes[row].annotate(f'{(height*100).round(2)}%', (bar.get_x() + bar.get_width() / 2., 0.02), ha='center', va='bottom', fontsize=25, color='black', xytext=(0, 0), textcoords='offset points', rotation=90)                                        
                            
            # if performance == 'average_latency':
            #     sns.barplot(x='dynamic', y='median_latency', hue='blockchain', data=grouped_df, legend='brief', palette='dark:black', alpha=0.9, hatch='//', fill=False, linewidth=1.3)        
                                    
            # palette=custom_colors, edgecolor='white', 
            # if row == len(performances)-1:
            #     axes[row].set_xlabel('Dynamics', fontsize=20)    
            # #     axes[row].set_xticks(axes[row].get_xticks())
            # #     axes[row].set_xticklabels(axes[row].get_xticklabels(), fontsize=18)
            # else: 
            axes[row].set_xlabel('')
                # axes[row].set_xticklabels('')  
            
            axes[row].set_xticks(axes[row].get_xticks())
            xticklabels = axes[row].get_xticklabels()
            new_labels = []
            for xtick in xticklabels:
                if xtick.get_text() == '0':
                    new_labels.append(f'no_{folder}')
                elif xtick.get_text() == '30':
                    new_labels.append(f'{folder}_30')
                elif xtick.get_text() == '20':
                    new_labels.append(f'{folder}_20')
                elif xtick.get_text() == '10':
                    new_labels.append(f'{folder}_10')
                else:
                    new_labels.append(xtick.get_text())
            axes[row].set_xticklabels(new_labels, fontsize=23)
                                    
            # plt.xticks(fontsize=14)
            # plt.yticks(fontsize=14)
            if performance == 'average_latency':
                ylabel = 'Block Finality (s)'
                axes[row].set_ylim(0, 200)  # Set the y-axis limits
            elif performance == 'average_throughput':
                ylabel = 'TPS'
            else:
                ylabel = 'Commit Ratio'
            axes[row].set_ylabel(ylabel, fontsize=26)                        
            axes[row].set_yticks(axes[row].get_yticks())
            axes[row].set_yticklabels(axes[row].get_yticklabels(), fontsize=23)
            
            axes[row].grid(axis='y', linestyle='--', alpha=0.7)
            axes[row].set_axisbelow(True) 

        # plt.suptitle(f'{topology.capitalize()}', fontsize=18, y=1.07)

        for ax in axes.flat:
            if ax.get_legend() is not None:
                ax.get_legend().remove()

        blockchain_handles, blockchain_labels = axes[0].get_legend_handles_labels()
        # legend = fig.legend(blockchain_handles, blockchain_labels, loc='upper center', bbox_to_anchor=(0.5, 0.97), fancybox=True, shadow=True, ncols=(len(blockchain_labels)), prop={'size': 24})

        plt.subplots_adjust(hspace=0.2)
        # plt.subplots_adjust(top=0.2, bottom=0.1, left=0.1, right=0.2, hspace=0.2, wspace=0.5)

        plt.tight_layout()  
        # plt.yscale('log')  

        plt.savefig(f'results/plot/performance/full-mesh-dynamic-{folder}-plot.pdf')
        plt.savefig(f'results/plot/performance/full-mesh-dynamic-{folder}-plot.png', dpi=300)
        # plt.savefig(f'results/plot/performance/full-mesh-dynamic-{folder}-plot.pdf', bbox_extra_artists=(legend,), bbox_inches='tight')
        # plt.savefig(f'results/plot/performance/full-mesh-dynamic-{folder}-plot.png', dpi=300, bbox_extra_artists=(legend,), bbox_inches='tight')
        plt.close()  