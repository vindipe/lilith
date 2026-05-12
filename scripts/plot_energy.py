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

energy_workloads = ['PayPal', 'VISA', 'GAFAM']
df = df[df['workload'].isin(energy_workloads)]

df["avg_node_energy"] = df["energy"] / (df["network_size"] * 10)

df['linearity'] = df['network_size']
df['network_size'] = df['network_size'].replace({1: '10 nodes', 4: '40 nodes'})

df["avg_transaction_energy"] = np.where(
    df["commit_number"] == 0,
    0,
    df["energy"] / df["commit_number"]
)

for val in ['energy', 'avg_node_energy', 'avg_transaction_energy']:
    for blockchain in blockchains:

        refined_topology_df = df[df['dataset'] == '2023']
        refined_topology_df = refined_topology_df[refined_topology_df['link_strategy'] == 'hop']
        # refined_topology_df = refined_topology_df[refined_topology_df['delay'] == 1]
        # refined_topology_df = refined_topology_df[refined_topology_df['network_size'] == size]
        # refined_topology_df = refined_topology_df[refined_topology_df['congestion'] == 0]
        refined_topology_df = refined_topology_df[refined_topology_df['secondaries'] == 10]
        refined_topology_df = refined_topology_df[refined_topology_df['cores'] == 8]
        refined_topology_df = refined_topology_df[refined_topology_df['ram'] == 16]
        refined_topology_df = refined_topology_df[refined_topology_df['dynamic'] == 0]
        # print(refined_topology_df)
        refined_topology_df = refined_topology_df[refined_topology_df['blockchain'] == blockchain]


        # grouped_df = workload_df.groupby('hash').agg({
            # 'run': 'max',

        grouped_df = refined_topology_df.groupby(['blockchain', 'mode', 'workload', 'cores', 'ram', 'secondaries', 'dataset', 'link_strategy', 'network_size', 'dynamic']).agg({
            val: 'mean',
            'commit_number': 'mean',
            # 'percentage_difference': 'mean'
            # 'MiB-Rx': 'mean'
        }).reset_index()

        if val == 'avg_node_energy':
            for idx, row in grouped_df.iterrows():
                # if row['blockchain'] == 'Solana' and row['workload'] in ['VISA', 'PayPal']:
                #     continue

                # if row['commit_number'] == 0:
                #     grouped_df.loc[idx, 'percentage_difference'] = None
                #     continue

                if row['network_size'] == '10 nodes':
                    expected_energy = row['avg_node_energy'] / 4

                    condition = (grouped_df['blockchain'] == row['blockchain']) & \
                                (grouped_df['mode'] == row['mode']) & \
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
                        percentage_diff = expected_energy

                        grouped_df.loc[row2.index, 'percentage_difference'] = percentage_diff
                    else:
                        print(f"No correspondence {idx} with network_size == 4")

                    # time.sleep(1)

            grouped_df.loc[grouped_df["network_size"] == '10 nodes', "percentage_difference"] = None

        # if val == 'energy':
        #     for idx, row in grouped_df.iterrows():
        #         # if row['blockchain'] == 'Solana' and row['workload'] in ['VISA', 'PayPal']:
        #         #     continue

        #         if row['commit_number'] == 0:
        #             grouped_df.loc[idx, 'percentage_difference'] = None
        #             continue

        #         if row['network_size'] == '10 nodes':
        #             condition = (grouped_df['blockchain'] == row['blockchain']) & \
        #                         (grouped_df['mode'] == row['mode']) & \
        #                         (grouped_df['workload'] == row['workload']) & \
        #                         (grouped_df['cores'] == row['cores']) & \
        #                         (grouped_df['ram'] == row['ram']) & \
        #                         (grouped_df['secondaries'] == row['secondaries']) & \
        #                         (grouped_df['dataset'] == row['dataset']) & \
        #                         (grouped_df['link_strategy'] == row['link_strategy']) & \
        #                         (grouped_df['dynamic'] == row['dynamic']) & \
        #                         (grouped_df['network_size'] == '40 nodes')

        #             row2 = grouped_df[condition]

        #             if not row2.empty:
        #                 percentage_diff = ((row2['energy'].iloc[0] - row['energy']) / row['energy']) * 100

        #                 grouped_df.loc[row2.index, 'percentage_difference'] = percentage_diff
        #             else:

        #             # time.sleep(1)

        #     grouped_df.loc[grouped_df["network_size"] == '10 nodes', "percentage_difference"] = None

        # print(df[df["network_size"] == 4])
        # exit(1)

        # print(grouped_df)

        # grouped_df['MiB-Tx'] = grouped_df['MiB-Tx'].astype(int)
        # grouped_df['MiB-Rx'] = grouped_df['MiB-Rx'].astype(int)

        # cols_to_remove = ['blockchain', 'workload', 'commit_number', 'abort_number', 'submit_number']
        # grouped_df.drop(columns=cols_to_remove, inplace=True)
        # print(grouped_df)
        # grouped_df.to_csv(f"{workload}-tmp.csv", index=False)

        fig, axes = plt.subplots(nrows=len(energy_workloads), ncols=1, figsize=(20, 25))
        # Flatten axes to iterate over them
        axes = axes.flatten()
        # axes[row].set_yscale('log')
        custom_colors = ['#f1a340', '#d8daeb']

        for row, workload in enumerate(energy_workloads):
            tmp_df = grouped_df[grouped_df['workload'] == workload]
            # print(tmp_df)
            # sns.barplot(x='mode', y='network', hue='verse', data=grouped_df, legend='brief', palette=custom_colors)
            # y=performance, hue='blockchain'

            if val == 'avg_node_energy':
                # if blockchain == 'Solana' and workload != 'GAFAM':

                # if not skip_lineplot:
                    # ax2 = axes[row].twinx()
                    sns.lineplot(x='mode', y='percentage_difference', data=tmp_df, ax=axes[row], color='grey', linestyle='dashed', marker='x', linewidth = 2.5, label='average · 10/40', markersize=26, markeredgecolor='black', markeredgewidth=5)
                    # ax2.legend(fontsize=23, loc='upper right')
                    # ax2.set_ylabel('Energy variability (kWh)', fontsize=36)
                    # ax2.set_ylim(-0.25, 0.25)  # Set the y-axis limits
                    # ax2.set_yticks(ax2.get_yticks())
                    # ax2.set_yticklabels(ax2.get_yticklabels(), fontsize=34)

            # if val == 'energy':
            #     # if blockchain == 'Solana' and workload != 'GAFAM':
            #     #     skip_lineplot = True

            #     # if not skip_lineplot:
            #         ax2 = axes[row].twinx()
            #         sns.lineplot(x='mode', y='percentage_difference', data=tmp_df, ax=ax2, color='grey', linestyle='dashed', marker='o', linewidth = 2.5, label='left y-axis', markersize=20, markerfacecolor='black')
            #         ax2.legend(fontsize=23, loc='upper right')
            #         ax2.set_ylabel('Energy scalability (%)', fontsize=36)
            #         ax2.set_ylim(-60, 60)  # Set the y-axis limits
            #         ax2.set_yticks(ax2.get_yticks())
            #         ax2.set_yticklabels(ax2.get_yticklabels(), fontsize=34)

            sns.barplot(x='mode', y=val, hue='network_size', data=tmp_df, legend='brief', palette=custom_colors, ax=axes[row], width=0.6)

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
            bars = bars[:len(bars) - 2]
            heights = [bar.get_height() for bar in bars]

            # Iterate over the bars and add 'X' label for bars with height 0
            if val != 'avg_transaction_energy':
                for bar, height in zip(bars, heights):
                    if height == 0:
                        index = bars.index(bar)  # Get the index of the current bar
                        # blockchain_name = grouped_df['blockchain'].iloc[index]  # Get the blockchain name from the dataframe
                        axes[row].text(bar.get_x() + bar.get_width() / 2, height, f'TPS: no-commit', ha='center', va='bottom', fontsize=32, rotation=90)
                    else:
                        # if len(tmp_df.loc[tmp_df[val] == height, 'commit_number'].values) > 1:
                        commit = tmp_df.loc[tmp_df[val] == height, 'commit_number'].values[0]
                        if int(commit) == 0:
                            axes[row].annotate(f'{(height.round(1))} | TPS: no-commit', (bar.get_x() + bar.get_width() / 2., 0.0001), ha='center', va='bottom', fontsize=32, color='black', xytext=(0, 0), textcoords='offset points', rotation=90)
                        else:
                            axes[row].annotate(f'{(height.round(1))} | TPS: {int(commit)}', (bar.get_x() + bar.get_width() / 2., 0.0001), ha='center', va='bottom', fontsize=32, color='black', xytext=(0, 0), textcoords='offset points', rotation=90)
            else:
                for bar, height in zip(bars, heights):
                    if height == 0 or height == 0.0:
                        index = bars.index(bar)  # Get the index of the current bar
                        # blockchain_name = grouped_df['blockchain'].iloc[index]  # Get the blockchain name from the dataframe
                        # axes[row].text(bar.get_x() + bar.get_width() / 2, height, f'FAILED', ha='center', va='bottom', fontsize=32, rotation=90)
                        axes[row].annotate('TPS: no-commit', (bar.get_x() + bar.get_width() / 2., 0.0001), ha='center', va='bottom', fontsize=32, color='black', xytext=(0, 0), textcoords='offset points', rotation=90)
                    else:
                        # print(tmp_df.loc[tmp_df['avg_transaction_energy'] == height, 'commit_number'].values)
                        commit = tmp_df.loc[tmp_df['avg_transaction_energy'] == height, 'commit_number'].values[0]
                        if int(commit) == 0:
                            axes[row].annotate(f'{(height.round(6))} | TPS: no-commit', (bar.get_x() + bar.get_width() / 2., 0.0001), ha='center', va='bottom', fontsize=32, color='black', xytext=(0, 0), textcoords='offset points', rotation=90)
                        else:
                            axes[row].annotate(f'{(height.round(6))} | TPS: {int(commit)}', (bar.get_x() + bar.get_width() / 2., 0.0001), ha='center', va='bottom', fontsize=32, color='black', xytext=(0, 0), textcoords='offset points', rotation=90)


            # palette=custom_colors, edgecolor='white',
            if row == len(energy_workloads)-1:
                # axes[row].set_xlabel('Network Topologies - Total Network Energy', fontsize=36)
                axes[row].set_xticks(axes[row].get_xticks())
                axes[row].set_xticklabels(axes[row].get_xticklabels(), fontsize=34)
            else:
                axes[row].set_xlabel('')
                axes[row].set_xticklabels('')

            # axes[row].set_xlabel('')

            # axes[row].set_yticklabels(fontsize=23)

            if val == 'energy':
                axes[row].set_ylim(0, 30)  # Set the y-axis limits
                axes[row].set_yticks(axes[row].get_yticks())
                axes[row].set_yticklabels(axes[row].get_yticklabels(), fontsize=34)

                # ticks = axes[row].get_yticks()
                # axes[row].set_yticks(ticks)
            elif val == 'avg_node_energy':
                axes[row].set_ylim(0, 3)  # Set the y-axis limits
                axes[row].set_yticks(axes[row].get_yticks())
                axes[row].set_yticklabels(axes[row].get_yticklabels(), fontsize=34)

                # ticks = axes[row].get_yticks()
                # axes[row].set_yticks(ticks)
            elif val == 'avg_transaction_energy':
                axes[row].set_ylim(0.0001, 1)
                ticks = [0.0001, 0.001, 0.01, 0.1, 1]
                axes[row].set_yticks(ticks)
                axes[row].set_yscale('log')

                # axes[row].yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: f"{y:.1e}"))
                axes[row].tick_params(axis='y', labelsize=34)  # Applica fontsize uniforme


            # plt.xticks(fontsize=14)
            # plt.yticks(fontsize=14)

            # axes[row].set_yticks(fontsize=23)
            # fig.text(0.15, 0.5, 'Energy Consumption kWh', fontsize=28, va='center', rotation='vertical')
            axes[row].set_ylabel(f'{workload} (kWh)', fontsize=36, labelpad=10)

            # if val != 'avg_transaction_energy':
            #     # Converti i tick in float con la precisione desiderata (2 decimali)
            #     axes[row].set_yticklabels([f'{int(tick)}' for tick in ticks], fontsize=26)
            # else:
            #     axes[row].set_yticks(axes[row].get_yticks())
            #     axes[row].set_yticklabels(axes[row].get_yticklabels(), fontsize=26)

            # axes[row].set_yticklabels([int(float(label.get_text())) for label in axes[row].get_yticklabels()], fontsize=23)
            # axes[row].set_yticklabels(axes[row].get_yticklabels(), fontsize=12)
            # axes[row].set_yticklabels([print(label) for label in axes[row].get_yticklabels()], fontsize=12)

            axes[row].grid(axis='y', linestyle='--', alpha=0.7)
            axes[row].set_axisbelow(True)

        # plt.suptitle(f'{topology.capitalize()}', fontsize=18, y=1.07)

        # axes[row].set_xlabel('Network Topologies', fontsize=36)
        if val == 'energy':
            axes[row].set_xlabel('(A) - Network topologies - Total kWh over all nodes', fontsize=36)
        elif val == 'avg_node_energy':
            axes[row].set_xlabel('(B) - Network topologies - Average kWh per node', fontsize=36)
        elif val == 'avg_transaction_energy':
            axes[row].set_xlabel('(C) - Network topologies - Average kWh per transaction', fontsize=36)
        for ax in axes.flat:
            if ax.get_legend() is not None:
                ax.get_legend().remove()

        verse_handles, verse_labels = axes[0].get_legend_handles_labels()

        if val == 'avg_node_energy':
            desired_order = ['10 nodes', 'average · 10/40', '40 nodes']

            order_indices = [verse_labels.index(label) for label in desired_order]

            # Riordina handles e labels
            verse_handles = [verse_handles[i] for i in order_indices]
            verse_labels = [verse_labels[i] for i in order_indices]

        legend = fig.legend(verse_handles, verse_labels, loc='upper center', bbox_to_anchor=(0.5, 0.92), fancybox=True, shadow=True, ncols=(len(verse_labels)), prop={'size': 30})

        # plt.subplots_adjust(bottom=0.8)
        # plt.subplots_adjust(left=0.15, hspace=0.3)

        # plt.tight_layout()
        # plt.yscale('log')

        plt.savefig(f'results/plot/energy/energy-{blockchain}-{val}-plot.pdf', bbox_extra_artists=(legend,), bbox_inches='tight')
        plt.savefig(f'results/plot/energy/energy-{blockchain}-{val}-plot.png', dpi=300, bbox_extra_artists=(legend,), bbox_inches='tight')
        plt.close()


# df['linearity'] = df['network_size']

from matplotlib.patches import Circle, RegularPolygon
from matplotlib.path import Path
from matplotlib.projections import register_projection
from matplotlib.projections.polar import PolarAxes
from matplotlib.spines import Spine
from matplotlib.transforms import Affine2D

def radar_factory(num_vars, frame='polygon'):
    theta = np.linspace(0, 2 * np.pi, num_vars, endpoint=False)

    class RadarTransform(PolarAxes.PolarTransform):
        def transform_path_non_affine(self, path):
            if path._interpolation_steps > 1:
                path = path.interpolated(num_vars)
            return Path(self.transform(path.vertices), path.codes)

    class RadarAxes(PolarAxes):
        name = 'radar'
        PolarTransform = RadarTransform

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.set_theta_zero_location('N')

        def fill(self, *args, closed=True, **kwargs):
            return super().fill(closed=closed, *args, **kwargs)

        def plot(self, *args, **kwargs):
            lines = super().plot(*args, **kwargs)
            for line in lines:
                self._close_line(line)

        def _close_line(self, line):
            x, y = line.get_data()
            if x[0] != x[-1]:
                x = np.append(x, x[0])
                y = np.append(y, y[0])
                line.set_data(x, y)

        def set_varlabels(self, labels):
            self.set_thetagrids(np.degrees(theta), labels)

        def _gen_axes_patch(self):
            if frame == 'polygon':
                return RegularPolygon((0.5, 0.5), num_vars, radius=0.5, edgecolor="k")
            else:
                return super()._gen_axes_patch()

        def _gen_axes_spines(self):
            if frame == 'polygon':
                spine = Spine(self, 'circle', Path.unit_regular_polygon(num_vars))
                spine.set_transform(Affine2D().scale(0.5).translate(0.5, 0.5) + self.transAxes)
                return {'polar': spine}
            else:
                return super()._gen_axes_spines()

    register_projection(RadarAxes)
    return theta


for val in ['energy', 'avg_node_energy', 'avg_transaction_energy']:

    # df[val] = normalize(df[val])
    # df['commit_number'] = normalize(df['commit_number'])
    # df['linearity'] = normalize(df['linearity'])

    # df['ratio'] = (df[val] / df['commit_number']) / df['linearity']

    # df['ratio'] = normalize(df['ratio'])

    for topology in topologies:
        for workload in workloads:
            refined_topology_df = df[df['dataset'] == '2023']
            refined_topology_df = refined_topology_df[refined_topology_df['link_strategy'] == 'hop']
            # refined_topology_df = refined_topology_df[refined_topology_df['delay'] == 1]
            # refined_topology_df = refined_topology_df[refined_topology_df['network_size'] == size]
            # refined_topology_df = refined_topology_df[refined_topology_df['congestion'] == 0]
            refined_topology_df = refined_topology_df[refined_topology_df['secondaries'] == 10]
            refined_topology_df = refined_topology_df[refined_topology_df['cores'] == 8]
            refined_topology_df = refined_topology_df[refined_topology_df['ram'] == 16]
            refined_topology_df = refined_topology_df[refined_topology_df['dynamic'] == 0]
            # print(refined_topology_df)
            refined_topology_df = refined_topology_df[refined_topology_df['mode'] == topology]
            refined_topology_df = refined_topology_df[refined_topology_df['workload'] == workload]
            # refined_topology_df = refined_topology_df[refined_topology_df['blockchain'] == blockchain]

            # grouped_df = workload_df.groupby('hash').agg({
                # 'run': 'max',

            # grouped_df = refined_topology_df.groupby(['blockchain', 'mode', 'workload', 'cores', 'ram', 'secondaries', 'dataset', 'link_strategy', 'network_size', 'dynamic']).agg({
            #     val: 'mean',
            #     # 'MiB-Rx': 'mean'
            # }).reset_index()

            data_size_1 = refined_topology_df[refined_topology_df['linearity'] == 1].groupby('blockchain')[val].mean()
            data_size_4 = refined_topology_df[refined_topology_df['linearity'] == 4].groupby('blockchain')[val].mean()

            # print(data_size_1)
            # print()
            # print(data_size_4)

            categories = blockchains
            n_categories = len(categories)

            theta = radar_factory(n_categories, frame='polygon')


            # angles = [n / float(n_categories) * 2 * pi for n in range(n_categories)]
            # angles += angles[:1]

            values_size_1 = data_size_1.reindex(categories).fillna(0).tolist()
            values_size_4 = data_size_4.reindex(categories).fillna(0).tolist()
            # values_size_1 += values_size_1[:1]
            # values_size_4 += values_size_4[:1]

            fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='radar'))

            ax.plot(theta, values_size_1, label='10 nodes', linewidth=6, linestyle='solid', color='#f1a340')
            ax.fill(theta, values_size_1, alpha=0.8, color='#f1a340')

            ax.plot(theta, values_size_4, label='40 nodes', linewidth=6, linestyle='solid', color='#d8daeb')
            ax.fill(theta, values_size_4, alpha=0.8, color='#d8daeb')

            # ax.set_xticks(angles[:-1])
            ax.set_varlabels(categories)
            ax.set_xticklabels(categories, fontsize=35, fontweight='bold')
            for label in ax.get_xticklabels():
                label.set_x(label.get_position()[0] - 0.2)

            # for spine in ax.spines.values():
            #     spine.set_linewidth(2)
            #     spine.set_color('grey')

            ax.xaxis.grid(True, linewidth=1, color='black')
            # ax.yaxis.grid(True, linewidth=2)

            if val == 'energy':
                ax.set_ylim(0, 30)  # Set the y-axis limits
                ax.set_yticks(ax.get_yticks())
                ax.set_yticklabels(ax.get_yticklabels(), fontsize=24)

                # ticks = ax.get_yticks()
                # ax.set_yticks(ticks)
            elif val == 'avg_node_energy':
                ax.set_ylim(0, 3)  # Set the y-axis limits
                ax.set_yticks(ax.get_yticks())
                ax.set_yticklabels(ax.get_yticklabels(), fontsize=24)

                # ticks = ax.get_yticks()
                # ax.set_yticks(ticks)
            elif val == 'avg_transaction_energy':
                ax.set_ylim(0.0001, 1)
                ticks = [0.0001, 0.001, 0.01, 0.1, 1]
                ax.set_yticks(ticks)
                ax.set_yscale('log')

                # ax.yaxis.set_major_formatter(ticks.FuncFormatter(lambda y, _: f"{y:.1e}"))
                ax.tick_params(axis='y', labelsize=28)
                for label in ax.get_yticklabels():
                    label.set_x(label.get_position()[0] + 0.2)


            # ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
            # ax.set_yticklabels(["0.2", "0.4", "0.6", "0.8", "1.0"], color="grey", size=8)
            # if val == 'energy':
            #     # ax.set_xlabel(f'{topology} - {workload} - Total over all nodes', size=23, color='black', loc='center')
            #     ax.set_xlabel(f'{topology} - {workload}', size=38, color='black', loc='center', labelpad=20)
            # elif val == 'avg_node_energy':
            #     # ax.set_xlabel(f'{topology} - {workload} - Average per node', size=23, color='black', loc='center')
            #     ax.set_xlabel(f'{topology} - {workload}', size=38, color='black', loc='center', labelpad=20)
            # if val == 'avg_transaction_energy':
            #     # ax.set_xlabel(f'{topology} - {workload} - Average per transaction', size=23, color='black', loc='center')
            ax.set_xlabel(f'{topology} - {workload}', size=35, color='black', loc='center', labelpad=-20)

            # ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15), ncols=(2), fancybox=True, shadow=True, prop={'size': 26})

            plt.tight_layout()

            plt.savefig(f'results/plot/energy/energy-{topology}-{workload}-{val}-plot.pdf', bbox_inches='tight')
            plt.savefig(f'results/plot/energy/energy-{topology}-{workload}-{val}-plot.png', dpi=300, bbox_inches='tight')
            plt.close()