import os
import pandas as pd
import json
import argparse
import time
import re
from datetime import datetime
import seaborn as sns
import matplotlib.pyplot as plt
import calendar
import numpy as np
import matplotlib.dates as mdates


def abbreviate_regions(input_string):
    output_string = input_string.replace("south", "s")
    output_string = output_string.replace("north", "n")
    output_string = output_string.replace("east", "e")
    output_string = output_string.replace("west", "w")
    return output_string


df = pd.read_csv('misc/cloudping/ping.csv')

df['src_region'] = df['src_region'].map(abbreviate_regions)
df['dst_region'] = df['dst_region'].map(abbreviate_regions)

df['origin'] = pd.to_datetime(df['origin'])
df['month_year'] = df['origin'].dt.to_period('M')
# df = df[df['month_year'].isin(['2023-04', '2023-09', '2023-12', '2024-03'])]
# df = df[df['origin'].dt.month.isin([4, 7, 11, 3])]
# df = df[~((df['origin'].dt.month == 4) & (df['origin'].dt.year == 2024))]
# print(df['month_year'])
month_year = df['month_year'].unique()

grouped_df = df.groupby(['src_region', 'dst_region', 'month_year']).agg({'ping_avg': 'mean'}).reset_index()
grouped_df['std_dev'] = df.groupby(['src_region', 'dst_region', 'month_year'])['ping_avg'].std().reset_index(drop=True)

# print(grouped_df)

# for index, row in grouped_df.iterrows():
#     corresponding_row = grouped_df[(grouped_df['src_region'] == row['dst_region']) & (grouped_df['dst_region'] == row['src_region'])]
#     if not corresponding_row.empty:
#         grouped_df.at[index, 'src_region'], grouped_df.at[index, 'dst_region'] = grouped_df.at[index, 'dst_region'], grouped_df.at[index, 'src_region']

# df = grouped_df.groupby(['src_region', 'dst_region', 'month_year']).agg({'ping_avg': 'mean', 'std_dev': 'std'}).reset_index()
# df['std_dev'] = grouped_df.groupby(['src_region', 'dst_region', 'month_year'])['ping_avg'].std().reset_index(drop=True)

# print(df)


# fig, axes = plt.subplots(3, 4, figsize=(18, 15))
fig, axes = plt.subplots(1, 4, figsize=(21, 5))
plt.subplots_adjust(wspace=0.01, hspace=0.01)

# cmap = sns.light_palette("black", as_cmap=True)  # Creiamo una scala di grigio a partire dal nero
cmap = sns.dark_palette("gray", as_cmap=True)  # Creiamo una scala di grigio scuro

row_index=0
col_index=0

for pair in month_year:
    plt.subplots_adjust(wspace=0.01, hspace=0.01)
    df_month = grouped_df[grouped_df['month_year'] == pair]  # Selezioniamo solo i dati relativi a quel mese

    month_name = calendar.month_name[pair.month].capitalize()
    year = pair.year

    sns.scatterplot(data=df_month, x='src_region', y='dst_region', size=df_month['ping_avg'], sizes=(50, 500), legend='brief', palette=cmap, hue='ping_avg', ax=axes[col_index])
    sns.scatterplot(data=df_month, x='src_region', y='dst_region', size=df_month['std_dev'], sizes=(100, 800), legend='brief', color='black', hue='std_dev', marker='_', linewidths=2, ax=axes[col_index])

    axes[col_index].set_title(f'{month_name} {year}', fontsize=17)

    if row_index == 0:
        axes[col_index].set_xticklabels(axes[col_index].get_xticklabels(), rotation=25, ha='right', fontsize=14)
    if col_index == 0:
        axes[col_index].set_yticklabels(axes[col_index].get_yticklabels(), ha='right', fontsize=16)

    for i in range(1):
        for j in range(4):
            ax = axes[j]
            if j != 0:  # Se la colonna non è la prima
                ax.set_yticks([])  # Rimuovi i ticks sull'asse y
            # if i != 2:  # Se la riga non è l'ultima
            #     ax.set_xticks([])  # Rimuovi i ticks sull'asse x

    col_index += 1
    if col_index == 4:
        col_index = 0
        row_index += 1

# Rimuovi le legende dai plot
for ax in axes.flat:
    ax.get_legend().remove()

ping_avg_handles, ping_avg_labels = axes[0].get_legend_handles_labels()
# print(ping_avg_labels)
ping_avg_legend = fig.legend(ping_avg_handles, ping_avg_labels, loc='center left', title='Ping Avg | Std_Dev (ms)', bbox_to_anchor=(-0.15, 0.5), fancybox=True, shadow=True, ncol=2, prop={'size': 16}, title_fontsize=18)

# plt.tight_layout(rect=[0, 0, 1, 0.9])
plt.tight_layout()

plt.setp(axes, xlabel=None, ylabel=None)
# fig.suptitle('1 Year of AWS Cloud Latencies measurements', fontsize=16, y=0.95)
# plt.savefig('trimesters_latencies.png', bbox_inches='tight')
# plt.savefig('trimesters_latencies.pdf', dpi=300, bbox_inches='tight')

plt.savefig('results/img/trimesters_latencies.png', bbox_extra_artists=(ping_avg_legend,), bbox_inches='tight')
plt.savefig('results/img/trimesters_latencies.pdf', dpi=300, bbox_extra_artists=(ping_avg_legend,), bbox_inches='tight')



# fig, axes = plt.subplots(3, 4, figsize=(16, 12))
# cmap = sns.light_palette("black", as_cmap=True)  # Creiamo una scala di grigio a partire dal nero

# for month in months:
#     df_month = df[df['month'] == month]  # Selezioniamo solo i dati relativi a quel mese

#     # Creiamo un nuovo grafico per questo mese
#     plt.figure(figsize=(5, 3))
#     plt.title(f'{calendar.month_name[month].capitalize()}', fontsize=10)
#     # plt.xlabel('src_region')
#     # plt.ylabel('dst_region')

#     # Impostiamo una mappatura di colore per la scala di grandezza dei cerchi
#     # cmap = sns.color_palette("viridis", as_cmap=True)  # Scegliamo una mappatura di colore
#     cmap = sns.light_palette("black", as_cmap=True)  # Creiamo una scala di grigio a partire dal nero
#     # sizes = df_month['ping_avg'] * 5  # Aumentiamo la scala delle dimensioni
#     # sizes = sizes.clip(10, None)  # Limitiamo la dimensione minima dei cerchi a 10
#     sns.scatterplot(data=df_month, x='src_region', y='dst_region', size=df_month['ping_avg'], sizes=(1, 500), legend=False, palette=cmap, hue='ping_avg')

#     # Mostrare il plot per questo mese
#     # plt.tight_layout()
#     plt.xticks(rotation=45, ha='right', fontsize=7)
#     plt.yticks(rotation=45, ha='right', fontsize=7)
#     plt.xlabel('')
#     plt.ylabel('')

#     plt.savefig(f'cloud-{month}-latencies.png')
#     plt.savefig(f'cloud-{month}-latencies.pdf', dpi=300, bbox_inches='tight')


df = pd.read_csv('misc/cloudping/ping-complete.csv')

df['src_region'] = df['src_region'].map(abbreviate_regions)
df['dst_region'] = df['dst_region'].map(abbreviate_regions)

df['origin'] = pd.to_datetime(df['origin'])
df['month_year'] = df['origin'].dt.to_period('M')
# df = df[df['origin'].dt.month.isin([4, 7, 11, 3])]
# df = df[~((df['origin'].dt.month == 4) & (df['origin'].dt.year == 2024))]
month_year = df['month_year'].unique()

plt.figure(figsize=(10, 6))
for pair in month_year:
    month_name = calendar.month_name[pair.month].capitalize()
    year = pair.year

    ping_avg_month = df[df['month_year'] == pair]['ping_avg']
    ping_avg_month_sorted = np.sort(ping_avg_month)
    cdf = np.arange(1, len(ping_avg_month_sorted) + 1) / len(ping_avg_month_sorted)
    plt.plot(ping_avg_month_sorted, cdf, label=f"{month_name} {year}")

plt.xlabel('Ping Average')
plt.ylabel('Cumulative Distribution Function')
# plt.title('CDF of Ping Average by Month')
plt.legend()
plt.grid(True)

plt.savefig('results/img/cloud-cdf-latencies.png')
plt.savefig('results/img/cloud-cdf-latencies.pdf', dpi=300, bbox_inches='tight')
plt.clf()


# # ACM-REP
# df = pd.read_csv('misc/cloudping/ping.csv')

# df['src_region'] = df['src_region'].map(abbreviate_regions)
# df['dst_region'] = df['dst_region'].map(abbreviate_regions)

# df['origin'] = pd.to_datetime(df['origin'])
# df['month_year'] = df['origin'].dt.to_period('M')
# month_year = df['month_year'].unique()

# grouped_df = df.groupby(['src_region', 'dst_region', 'month_year']).agg({'ping_avg': 'mean'}).reset_index()
# grouped_df['std_dev'] = df.groupby(['src_region', 'dst_region', 'month_year'])['ping_avg'].std().reset_index(drop=True)

# # print(grouped_df)

# # for index, row in grouped_df.iterrows():
# #     corresponding_row = grouped_df[(grouped_df['src_region'] == row['dst_region']) & (grouped_df['dst_region'] == row['src_region'])]
# #     if not corresponding_row.empty:
# #         grouped_df.at[index, 'src_region'], grouped_df.at[index, 'dst_region'] = grouped_df.at[index, 'dst_region'], grouped_df.at[index, 'src_region']

# # df = grouped_df.groupby(['src_region', 'dst_region', 'month_year']).agg({'ping_avg': 'mean', 'std_dev': 'std'}).reset_index()
# # df['std_dev'] = grouped_df.groupby(['src_region', 'dst_region', 'month_year'])['ping_avg'].std().reset_index(drop=True)

# # print(df)


# fig, axes = plt.subplots(3, 4, figsize=(18, 15))
# plt.subplots_adjust(wspace=0.0001, hspace=0.0001)

# # cmap = sns.light_palette("black", as_cmap=True)  # Creiamo una scala di grigio a partire dal nero
# cmap = sns.dark_palette("gray", as_cmap=True)  # Creiamo una scala di grigio scuro

# row_index=0
# col_index=0

# for pair in month_year:
#     # plt.subplots_adjust(wspace=0.01, hspace=0.01)
#     df_month = grouped_df[grouped_df['month_year'] == pair]  # Selezioniamo solo i dati relativi a quel mese

#     month_name = calendar.month_name[pair.month].capitalize()
#     year = pair.year

#     sns.scatterplot(data=df_month, x='src_region', y='dst_region', size=df_month['ping_avg'], sizes=(50, 500), legend='brief', palette=cmap, hue='ping_avg', ax=axes[row_index, col_index])
#     sns.scatterplot(data=df_month, x='src_region', y='dst_region', size=df_month['std_dev'], sizes=(100, 800), legend='brief', color='black', hue='std_dev', marker='_', linewidths=2, ax=axes[row_index, col_index])

#     axes[row_index, col_index].set_title(f'{month_name} {year}', fontsize=17)

#     if row_index == 2:
#         axes[row_index, col_index].set_xticklabels(axes[row_index, col_index].get_xticklabels(), rotation=25, ha='right', fontsize=14)
#     if col_index == 0:
#         axes[row_index, col_index].set_yticklabels(axes[row_index, col_index].get_yticklabels(), ha='right', fontsize=16)

#     for i in range(3):
#         for j in range(4):
#             ax = axes[i, j]
#             if j != 0:  # Se la colonna non è la prima
#                 ax.set_yticks([])  # Rimuovi i ticks sull'asse y
#             if i != 2:  # Se la riga non è l'ultima
#                 ax.set_xticks([])  # Rimuovi i ticks sull'asse x

#     col_index += 1
#     if col_index == 4:
#         col_index = 0
#         row_index += 1

# # Rimuovi le legende dai plot
# for ax in axes.flat:
#     ax.get_legend().remove()

# ping_avg_handles, ping_avg_labels = axes[0, 0].get_legend_handles_labels()
# # print(ping_avg_labels)
# ping_avg_legend = fig.legend(ping_avg_handles, ping_avg_labels, loc='upper center', title='Ping Avg                                   |                                   Std_Dev (ms)', bbox_to_anchor=(0.53, 1.01), fancybox=True, shadow=True, ncol=len(ping_avg_labels), prop={'size': 16}, title_fontsize=18)

# # plt.tight_layout(rect=[0, 0, 1, 0.9])
# # plt.tight_layout()
# plt.tight_layout(pad=0.1, rect=[0, 0, 1, 0.94])

# plt.setp(axes, xlabel=None, ylabel=None)
# # fig.suptitle('1 Year of AWS Cloud Latencies measurements', fontsize=16, y=0.95)
# # plt.savefig('trimesters_latencies.png', bbox_inches='tight')
# # plt.savefig('trimesters_latencies.pdf', dpi=300, bbox_inches='tight')

# plt.savefig('results/img/ping_latencies.png', bbox_extra_artists=(ping_avg_legend,), bbox_inches='tight')
# plt.savefig('results/img/ping_latencies.pdf', dpi=300, bbox_extra_artists=(ping_avg_legend,), bbox_inches='tight')



# MIDDLEWARE
df = pd.read_csv('misc/cloudping/ping.csv')

df['src_region'] = df['src_region'].map(abbreviate_regions)
df['dst_region'] = df['dst_region'].map(abbreviate_regions)
regions = sorted(df['src_region'].unique())

df['origin'] = pd.to_datetime(df['origin'])

# df['month_year'] = df['origin'].dt.strftime('%B %Y')
# df['month_order'] = df['origin'].dt.to_period('M')
# df = df.sort_values(by='month_order')

# df['month_year'] = df['origin'].dt.to_period('M')
# df['month_year'] = df['month_year'].apply(lambda p: f"{calendar.month_name[p.month]} {p.year}")
# month_year = df['month_year'].unique()
# print(month_year)

df['origin'] = df['origin'].dt.to_period('D').dt.to_timestamp()

grouped_df = df.groupby(['src_region', 'dst_region', 'origin']).agg({'ping_avg': 'mean'}).reset_index()
grouped_df['std_dev'] = df.groupby(['src_region', 'dst_region', 'origin'])['ping_avg'].std().reset_index(drop=True)


fig, axes = plt.subplots(5, 2, figsize=(18, 12))
plt.subplots_adjust(wspace=0.0001, hspace=0.0001)
fig.text(0.09, 0.5, 'Standard Deviation of Daily Average Ping (ms)', va='center', rotation='vertical', fontsize=21)

# cmap = sns.light_palette("black", as_cmap=True)  # Creiamo una scala di grigio a partire dal nero
# cmap = sns.dark_palette("gray", as_cmap=True)  # Creiamo una scala di grigio scuro

row_index=0
col_index=0

for region in regions:
    # plt.subplots_adjust(wspace=0.01, hspace=0.01)
    df_region = grouped_df[(grouped_df['src_region'] == region) | (grouped_df['dst_region'] == region)]
    mask = df_region['dst_region'] == region
    df_region.loc[mask, ['src_region', 'dst_region']] = df_region.loc[mask, ['dst_region', 'src_region']].values

    # print(df_region)
    # df_region.to_csv("temp/temp.csv", index=False)

    ax = axes[row_index, col_index]

    # sns.stripplot(
    sns.lineplot(
        data=df_region,
        x='origin',
        y='std_dev',
        hue='dst_region',
        ax=ax,
        # dodge=True,
        # jitter=True,
        alpha=0.7,
        palette='tab10'
    )

    ax.set_yscale('log')
    ax.set_ylim(0.001, 60)
    # ax.set_ylim(0, 60)

    ax.set_title(f'AWS Source Region: {region}', fontsize=17)

    min_date = df_region['origin'].min()
    max_date = df_region['origin'].max()
    ax.set_xlim(min_date, max_date)

    # Formatter
    # ax.xaxis.set_major_locator(mdates.MonthLocator())
    # ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b '%y"))

    # print(row_index)
    if row_index == 4:
        ax.set_xticklabels(ax.get_xticklabels(), rotation=25, ha='right', fontsize=14)
    if col_index == 0:
        ax.set_yticklabels(ax.get_yticklabels(), ha='right', fontsize=16)

    for i in range(5):
        for j in range(2):
            ax = axes[i, j]

            xticks = ax.get_xticks()
            for x in xticks:
                ax.axvline(x=x, color='gray', linestyle='--', alpha=0.6, linewidth=1)
            ax.grid(True, axis='x')

            if j != 0:
                ax.set_yticks([])
            if i != 4:
                ax.set_xticks([])

    col_index += 1
    if col_index == 2:
        col_index = 0
        row_index += 1

# Rimuovi le legende dai plot
for ax in axes.flat:
    ax.get_legend().remove()

region_pair_handles, region_pair_labels = axes[0, 0].get_legend_handles_labels()
# print(region_pair_labels)
region_pair_legend = fig.legend(region_pair_handles, region_pair_labels, loc='upper center', title='AWS Destination Regions', bbox_to_anchor=(0.54, 1.03), fancybox=True, shadow=True, ncol=len(region_pair_labels), prop={'size': 16}, title_fontsize=18)

# plt.tight_layout(rect=[0, 0, 1, 0.9])
plt.tight_layout()
# plt.tight_layout(pad=0.1, rect=[0.05, 0, 0, 0.95])
# plt.tight_layout(pad=0.1, rect=[0.1, 0.05, 0.95, 0.95])
plt.subplots_adjust(left=0.14, top=0.91)

plt.setp(axes, xlabel=None, ylabel=None)
# fig.suptitle('1 Year of AWS Cloud Latencies measurements', fontsize=16, y=0.95)

plt.savefig('results/img/new_ping_latencies.png', bbox_extra_artists=(region_pair_legend,), bbox_inches='tight')
plt.savefig('results/img/new_ping_latencies.pdf', dpi=300, bbox_extra_artists=(region_pair_legend,), bbox_inches='tight')