import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import time as time
import sys


if len(sys.argv) != 5:
    print("Usage: python3 plotting.py machines_number path bandwidth dataset_type")
else:
    machines = sys.argv[1]
    df_path = sys.argv[2]
    bw = sys.argv[3]
    dataset = sys.argv[4]
    
df = pd.read_csv(f'{df_path}/kollaps-df.csv')

# df['k_latency_diff'] = df['k_latency'] - df['latency']
# df['k_throughput_diff'] = df['k_throughput'] - df['throughput']

# Find percentage differences
df['k_latency_diff_%'] = ((df['k_latency'] - df['latency']) / df['latency']) * 100
df['k_throughput_diff_%'] = ((df['k_throughput'] - df['throughput']) / df['throughput']) * 100
# df[['k_latency_diff_%', 'k_throughput_diff_%']] = df[['k_latency_diff_%', 'k_throughput_diff_%']].map(lambda x: 0 if abs(x) < 1e-5 or int(x) == 0 else x)
df[['k_latency_diff_%', 'k_throughput_diff_%']] = df[['k_latency_diff_%', 'k_throughput_diff_%']].map(lambda x: 0 if pd.notna(x) and (abs(x) < 1e-5 or int(x) == 0) else x)

df.to_csv(f'{df_path}/kollaps-df.csv', index=False) 

REGNAMES = {
    'af-south-1': "Cape Town",
    'ap-northeast-1': "Tokyo",
    'ap-south-1': "Mumbai",
    'ap-southeast-2': "Sydney",
    'eu-north-1': "Stockholm",
    'eu-south-1': "Milan",
    'me-south-1': "Bahrain",
    'sa-east-1': "Sao Paulo",
    'us-east-2': "Ohio",
    'us-west-2': "Oregon"
}

# Get index and columns unique indexes
index_values = np.unique(df[['src_region', 'dst_region']].values)
columns_values = np.unique(df[['src_region', 'dst_region']].values)

matrix_df = pd.DataFrame(index=index_values, columns=columns_values)

cmap_upper = sns.color_palette("gray_r", as_cmap=True)
cmap_lower = sns.color_palette("YlOrRd", as_cmap=True)

# data_columns = ['k_latency_diff', 'k_latency_diff_%']
data_columns = ['k_latency_diff_%']
fig, axes = plt.subplots(1, 2, figsize=(18, 11))

for idx, column in enumerate(data_columns):
    for i, row in df.iterrows():
        # print(row)
        matrix_df.at[row['src_region'], row['dst_region']] = row['latency']
        matrix_df.at[row['dst_region'], row['src_region']] = row[column]
        
    # print(matrix_df)

    # # Ora otteniamo la colonna 'col2' come array e la sistemiamo nella parte inferiore della matrice
    # col2_values = df[column].values
    # lower_triangle_indices = np.tril_indices(len(index_values), k=-1)
    # matrix_df.values[lower_triangle_indices] = col2_values

    matrix_df = matrix_df.astype(float)
    x_labels = matrix_df.columns.map(REGNAMES)
    y_labels = matrix_df.index.map(REGNAMES)

    vmin = matrix_df.min().min() - 0.05 * (matrix_df.max().max() - matrix_df.min().min())
    vmax = matrix_df.max().max() + 0.05 * (matrix_df.max().max() - matrix_df.min().min())

    heatmap = sns.heatmap(matrix_df, annot=True, fmt=".1f", cmap=cmap_upper, annot_kws={"size": 16}, cbar_kws={"shrink": 0.4},
                      xticklabels=x_labels, yticklabels=y_labels, vmin=vmin, vmax=vmax, ax=axes[idx])
    
    # Remove values bar
    heatmap.collections[0].colorbar.remove()

    # Modify color in lower triangle
    for i in range(matrix_df.shape[0]):
        for j in range(i + 1, matrix_df.shape[1]):
            cell_value = matrix_df.iloc[i, j]
            norm_value = (cell_value - vmin) / (vmax - vmin)
            color = cmap_lower(norm_value)
            heatmap.add_patch(plt.Rectangle((j, i), 1, 1, fill=True, color=color))

    title_suffix = 'Differences'
    if '%' in column:
        title_suffix = '% comparison'
        
    axes[idx].set_title(f'{title_suffix.capitalize()}', fontsize = 16)
    axes[idx].set_xticklabels(axes[idx].get_xticklabels(), rotation=45, fontsize=15)
    axes[idx].set_yticklabels(axes[idx].get_yticklabels(), rotation=-45, fontsize=15)
    axes[idx].set_xlabel('')
    axes[idx].set_ylabel('')

# plt.savefig('../img/kollaps_{}_heatmap.png'.format(column))            


# fig, axes = plt.subplots(1, 2, figsize=(22, 10))  # 1 riga, 2 colonne
# data_columns = ['k_throughput_diff', 'k_throughput_diff_%']
data_columns = ['k_throughput_diff_%']

for idx, column in enumerate(data_columns):
    idx += 1
    for i, row in df.iterrows():
        matrix_df.at[row['src_region'], row['dst_region']] = row['throughput']
        matrix_df.at[row['dst_region'], row['src_region']] = row[column]

    # col2_values = df[column].values    
    # print(col2_values)
    # lower_triangle_indices = np.tril_indices(len(index_values), k=-1)
    # print(lower_triangle_indices)
    # matrix_df.values[lower_triangle_indices] = col2_values

    matrix_df = matrix_df.astype(float)
    x_labels = matrix_df.columns.map(REGNAMES)
    y_labels = matrix_df.index.map(REGNAMES)

    vmin = matrix_df.min().min() - 0.05 * (matrix_df.max().max() - matrix_df.min().min())
    vmax = matrix_df.max().max() + 0.05 * (matrix_df.max().max() - matrix_df.min().min())   

    heatmap = sns.heatmap(matrix_df, annot=True, fmt=".1f", cmap=cmap_upper, annot_kws={"size": 16}, cbar_kws={"shrink": 0.8},
                      xticklabels=x_labels, yticklabels=False, vmin=vmin, vmax=vmax, ax=axes[idx])
    
    heatmap.collections[0].colorbar.remove()

    for i in range(matrix_df.shape[0]):
        for j in range(i + 1, matrix_df.shape[1]):
            cell_value = matrix_df.iloc[i, j]
            norm_value = (cell_value - vmin) / (vmax - vmin)
            color = cmap_lower(norm_value)
            heatmap.add_patch(plt.Rectangle((j, i), 1, 1, fill=True, color=color))
   
    title_suffix = 'Differences'
    if '%' in column:
        title_suffix = '% comparison'
        
    axes[idx].set_title(f'{title_suffix.capitalize()}', fontsize = 16)
    axes[idx].set_xticklabels(axes[idx].get_xticklabels(), rotation=45, fontsize=15)
    axes[idx].set_yticklabels(axes[idx].get_yticklabels(), rotation=-45, fontsize=15)
    axes[idx].set_xlabel('')
    axes[idx].set_ylabel('')  


# title_text = r'$\it{Iperf3}$'
# title_text += ' Latencies (ms) and Throughput (Mbps) heatmap comparison of Diablo\'s AWS measurements with Kollaps'
# fig.suptitle(title_text, fontsize=20)

# Legend for the lower part of the matrix
legend_text = f'* Upper triangle reflects {dataset.capitalize()}\'s AWS measurements, while the lower triangle illustrates the difference in Kollaps measurements'
legend_text += f'\n* Nodes bandwidth: {bw}Gbps'
legend_text += f'\n* Experiment executed with #{machines} nodes in the cluster'
fig.text(0.5, 0.04, legend_text, ha='center', va='center', fontsize=15)  # Modificato il valore 0.02 a 0.05
plt.tight_layout(rect=[0, 0.07, 1, 0.98])

# plt.savefig('./img/kollaps_{}_heatmap.png'.format(column)) 
plt.savefig(f'{df_path}/../img/kollaps-heatmap-{machines}.png', bbox_inches='tight')
plt.savefig(f'{df_path}/../img/kollaps-heatmap-{machines}.pdf', dpi=300, bbox_inches='tight')