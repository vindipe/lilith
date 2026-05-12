import pandas as pd
import matplotlib.pyplot as plt


def plot_combined_region_counts(dfs, switch_labels):
    plt.figure(figsize=(10, 6))

    # Itera attraverso i dataframes e le relative etichette
    for df, label in zip(dfs, switch_labels):
        # Conta il numero di occorrenze di ogni regione nelle colonne src_region e dst_region
        region_counts = pd.concat([df['src_region'], df['dst_region']]).value_counts()
        
        # Estrae solo i valori delle occorrenze
        counts = region_counts.values
        
        # Crea il plot per ogni dataframe
        plt.plot(counts, label=f'{label} switches')
    
    plt.title('Switch degree in Scale-free topology')
    plt.xlabel('Switch Number')
    plt.ylabel('Switch Degree')
    plt.xticks([0, 250, 500, 1000])
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"results/img/scale_free_power_law_plot.png")
    plt.savefig(f'results/img/scale_free_power_law_plot.pdf', dpi=500, bbox_inches='tight')

df_switch_250 = pd.read_csv("results/img/topo_data_250_tmp.csv")
df_switch_500 = pd.read_csv("results/img/topo_data_500_tmp.csv")
df_switch_1000 = pd.read_csv("results/img/topo_data_1000_tmp.csv")

# Crea e salva il plot combinato per i tre dataframes
dfs = [df_switch_250, df_switch_500, df_switch_1000]
switch_labels = [250, 500, 1000]
plot_combined_region_counts(dfs, switch_labels)
