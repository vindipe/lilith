import pandas as pd
import xml.etree.ElementTree as ET
import argparse
import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
import math
import random
import sys
import re
# import cartopy.crs as ccrs
# import netgraph
# import subprocess
import scipy as sp
# import os
# import yaml
import shutil
import time


def create_full_mesh_topology(df):        
    # All-to-All - standard    
    return df    
        
def create_scale_free_topology(df, mode):    
    # Initial switches = 3/10
        # Selected based on lower latency/higher throughput
    # New switch upon entry = random number between (2 and NUM_EXISTING_NODES - 1 until it remains less than MAX - 4)   
        # Based on throughput/latencies
    
    df_copy = df.copy()
    actual_links_df = pd.DataFrame()
    
    unique_regions = df_copy['src_region'].unique() 
    # print(len(unique_regions))
    max_regions = len(unique_regions)
    
    # switch iniziali = 3/10 || > 2
    switch_iniziali = max(2, int(max_regions*0.02))
    degree = 1
    
    # if max_regions < 500:
    #     degree = 1
    # elif 501 <= max_regions <= 1000:
    #     degree = 2

    if mode == 'scale-free-l':        
        # LATENCY -----------------------------------    
        # Calculate the sum of latencies for each region
        region_latency_sum = {}
        for region in unique_regions:
            region_latency_sum[region] = df_copy[df_copy['src_region'] == region]['latency'].sum()
            region_latency_sum[region] = df_copy[df_copy['src_region'] == region]['latency'].mean()

        # Sort the dictionary by minimum sum
        sorted_latency_sum = sorted(region_latency_sum.items(), key=lambda x: x[1])
        # print("Sorted latencies sum : ", sorted_latency_sum)

        # Take the top 3 values from the dictionary based on the region key
        actual_switches = [region for region, _ in sorted_latency_sum[:switch_iniziali]]
        # print("Switch iniziali:", actual_switches)             
    elif mode == 'scale-free-t':
        # THROUGHPUT -----------------------------------
        # Calculate the sum of latencies for each region
        region_throughput_sum = {}
        for region in unique_regions:
            # region_throughput_sum[region] = df_copy[df_copy['src_region'] == region]['throughput'].sum()
            region_throughput_sum[region] = df_copy[df_copy['src_region'] == region]['throughput'].mean()

        # Sort the dictionary by minimum sum
        sorted_throughput_sum = sorted(region_throughput_sum.items(), key=lambda x: x[1], reverse=True)
        print("Sorted THROUGHPUT sum : ", sorted_throughput_sum)

        # Take the first 3 values from the dictionary based on the region key
        actual_switches = [region for region, _ in sorted_throughput_sum[:switch_iniziali]]
        # print("Switch iniziali:", actual_switches)
    elif mode == 'scale-free-r':
        # RANDOM -----------------------------------    
        # Take the first 3 values from the dictionary based on the region key
        actual_switches = df_copy['src_region'].unique()[:switch_iniziali]
        actual_switches = actual_switches.tolist()
        # print("Switch iniziali:", actual_switches)
        

    actual_links_df = df_copy[df_copy['src_region'].isin(actual_switches) & df_copy['dst_region'].isin(actual_switches)]
    print(actual_links_df)    # dovrebbe essere = len(actual_switches)

    # Remove those in initial_switches from unique_regions
    unique_regions = [region for region in unique_regions if region not in actual_switches]

    # For each remaining switch in unique_regions
    for new_switch in unique_regions:
        
        # Calculate the degree of existing nodes
        dizionario_degrees = {}
        for region in actual_switches:
            region_degree = len(actual_links_df[(actual_links_df['src_region'] == region) | (actual_links_df['dst_region'] == region)])
            dizionario_degrees[region] = region_degree
            
        # print("English dictionary : ", dizionario_degrees)
        
        # Calculate link probability
        total_degree_sum = sum(dizionario_degrees.values())
        probabilities = {region: degree / total_degree_sum for region, degree in dizionario_degrees.items()}
        # print("Probabilities : ", probabilities)
        # sorted_probabilities = sorted(probabilities.items(), key=lambda x: x[1], reverse=True)
        # print("Sorted Probabilities : ", sorted_probabilities)
        
        regions_to_connect = []
        
        # prendo un valore random tra degree-1 e degree+1, con seed 443
        random.seed(443)    
        
        # node_prob = random.random()
        # # print(node_prob)
        # for _ in range(degree):
        #     accumulated_prob = 0            
        #     while accumulated_prob <= node_prob:
        #         node, prob = sorted_probabilities.pop(0)  # Prendi il primo nodo in sorted_probabilities
        #         accumulated_prob += prob
        #         sorted_probabilities.append((node, prob))  # Sposta quel nodo in fondo a sorted_probabilities
        #     regions_to_connect.append(node)  # Aggiungi quel nodo a regions_to_connect       
        
        regions_to_connect = random.choices(list(probabilities.keys()), weights=list(probabilities.values()), k=degree)
                        
        # print("Regions to Connect : ", regions_to_connect)
        # time.sleep(2)
        
        # Add the new switch and connections to the topology
        for region in regions_to_connect:
            new_link = df_copy[((df_copy['src_region'] == new_switch) | (df_copy['dst_region'] == new_switch)) & 
                                ((df_copy['src_region'] == region) | (df_copy['dst_region'] == region))]
            actual_links_df = pd.concat([actual_links_df, new_link], ignore_index=True)        
        
        actual_switches.append(new_switch)
        # print(actual_links_df)          

    # Count the number of occurrences of each region in the src_region and dst_region columns
    region_counts = pd.concat([actual_links_df['src_region'], actual_links_df['dst_region']]).value_counts()
    # print(region_counts)

    # Plot the counts of the regions
    region_counts.plot(kind='bar', color='skyblue')
    plt.title(f'Nodes degree in Scale-free with {switches} switches')
    plt.xlabel('Switch Name')
    plt.ylabel('Switch Degree')
    plt.xticks(rotation=45)  # Ruota le etichette sull'asse x per una migliore leggibilità
    plt.savefig(f"results/img/degree_scale_free_{switches}_{mode}.png")
    plt.savefig(f'results/img/degree_scale_free_{switches}_{mode}.pdf', dpi=500, bbox_inches='tight')
    
    # plt.figure(figsize=(10, 6))
    # plt.loglog(region_counts.values, 'b-', marker='o', markersize=3)
    # plt.title('Distribuzione del grado dei nodi (Scale-Free)')
    # plt.xlabel('Grado del nodo (log)')
    # plt.ylabel('Numero di nodi con quel grado (log)')
    # plt.grid(True, which="both", ls="--", lw=0.5)    
    
    # plt.savefig(f"results/img/plot_scale_free_2_{mode}.png")
    
    # edges = list(zip(actual_links_df['src_region'], actual_links_df['dst_region']))
    # G = nx.Graph()
    # G.add_edges_from(edges)
    # plt.figure(figsize=(40, 30))
    # pos = nx.fruchterman_reingold_layout(G)
    # edge_width = 0.1
    # nx.draw(G, pos, node_size=300, node_color='black')
    # nx.draw_networkx_edges(G, pos, width=edge_width, alpha=0.7, edge_color='black', arrows=True, arrowstyle='-|>')    
    # plt.title("Scale-Free Network")  
    # plt.tight_layout()      
    # plt.savefig(f"results/img/graph_scale_free_{switches}_{mode}.png")
    # plt.savefig(f'results/img/graph_scale_free_{switches}_{mode}.pdf', dpi=500, bbox_inches='tight')        
            
    return actual_links_df

# def create_hypercube_topology(df):    
#     # Hypercube 4D = 2^4 = 16 reduced to our 10 regions
#     # Here each switch will be connected to log2(#switches) OR 4
#     # Latencies/throughput were not used to define switches across dimensions
    
#     df_copy = df.copy()
#     df = pd.DataFrame()       

#     unique_regions = df_copy['src_region'].unique()        
        
#     # dimensions = 4  # 4-dimensional Hypercube    
#     dimensions = int(math.log2(df_copy['src_region'].nunique()))+1
#     print("Hypercube dimensions: ", dimensions)
#     node_vectors = {}  # Dictionary to store node vectors
    
#     # Populate the node_vectors dictionary with Region-Number pairs first
#     for i, region in enumerate(unique_regions):
#         node_vectors[region] = i
    
#     # Creating vectors for each region/node
#     for region in unique_regions:
#         binary_vector = format(node_vectors[region], f'0{dimensions}b')
#         node_vectors[region] = binary_vector
        
#     # print("Node Vectors : ", node_vectors)
    
#     # Creating links for the Hypercube
#     for node in unique_regions:
#         # Find the binary vector of the current node
#         current_node_vector = node_vectors[node]
#         # print("current_node_vector : ", current_node_vector)
        
#         # Determine neighbors of the current node based on Hypercube structure
#         for i in range(dimensions):
#             # Modify only one bit in the binary vector to find the neighbor
#             # print("list(current_node_vector) : ", list(current_node_vector))
#             neighbor_binary_vector = list(current_node_vector)            
#             neighbor_binary_vector[i] = '1' if neighbor_binary_vector[i] == '0' else '0'
#             print("neighbor_binary_vector[i] : ", neighbor_binary_vector[i])
#             neighbor_index = int(''.join(neighbor_binary_vector), 2)
#             # print("neighbor_index : ", neighbor_index)

#             # Check if the resulting neighbor is among the active nodes
#             while neighbor_index > 9:  # Assuming only the first 10 nodes are active
#                 # The neighbor is not among the active nodes, change another bit in the binary vector and recalculate the index
#                 # For instance, you can flip the bit in the next position
#                 i = (i + 1) % dimensions
#                 neighbor_binary_vector[i] = '1' if neighbor_binary_vector[i] == '0' else '0'
#                 neighbor_index = int(''.join(neighbor_binary_vector), 2)
#                 # print("Updated neighbor_index : ", neighbor_index)            
            
#             # Find the name of the region corresponding to the neighbor
#             for region, vector in node_vectors.items():
#                 # print("vector : ", vector)
#                 # print("neighbor_binary_vector : ", neighbor_binary_vector)
#                 if ''.join(neighbor_binary_vector) == vector:
#                     neighbor_region = region
#                     break            
#             print("neighbor_region : ", neighbor_region)
            
#             # Add the link to the DataFrame
#             link = df_copy[(df_copy['src_region'] == node) & (df_copy['dst_region'] == neighbor_region) | (df_copy['src_region'] == neighbor_region) & (df_copy['dst_region'] == node)]
            
#             # print("link : ", link)
#             df = pd.concat([df, link], ignore_index=True)    
            
#             # time.sleep(50)

#     df = df.drop_duplicates()            
#     print(df)

#     return df

def create_torus_topology(df, mode):
    # Torus 2D 2*5
    # each switch connects in 4 directions

    df_copy = df.copy()
    df = pd.DataFrame()    

    # unique_regions = df_copy['src_region'].unique()

    # create a 2x5 grid data structure
    unique_columns = df_copy['src_region'].nunique()/2
    columns = df_copy['src_region'].nunique()/2
    if isinstance(columns, float):
        columns = int(columns)+1       
    print("Torus 2 x", columns)
    grid = [[(i, j) for j in range(columns)] for i in range(2)]    

    if mode == 'torus-l':
        # LATENCY-BASED ------------------        
        # sort the dataset based on latencies
        df_copy = df_copy.sort_values(by='latency', ascending=True)
    elif mode == 'torus-t':
        # THROUGHPUT-BASED ----------------
        # sort the dataset based on latencies
        df_copy = df_copy.sort_values(by='throughput', ascending=False)   
         
    # take the first row
    df_row = df_copy.iloc[0]
    src_region = df_row['src_region']
    dst_region = df_row['dst_region']
    
    # Insert src and dst in the grid
    grid[0][0] = src_region
    grid[1][0] = dst_region
    # print("Grid : ", grid)
    
    df = pd.concat([df, df_row.to_frame().T], ignore_index=True)
    # df = df.append(df_row)
    print(df)    
    
    # Create a list to keep track of regions already used
    regioni_usate = [src_region, dst_region]

    for col in range(columns):
        for row in range(2):
            # Skip the first column
            if col == 0:
                continue
            if col == columns-1 and isinstance(unique_columns, float) and row == 1:
                continue
            
            # Get the previous region
            prev_region = grid[row][col - 1]
            print("Prev region : ", prev_region)
            
            # Filter the dataframe to exclude regions already considered
            df_subset = df_copy[(df_copy['src_region'] == prev_region) | (df_copy['dst_region'] == prev_region)]
            print("Subset #1  : ", df_subset)
            
            if mode == 'torus-l':
                # LATENCY-BASED ------------------        
                # sort the dataset based on latencies
                df_subset = df_subset.sort_values(by='latency', ascending=True)
            elif mode == 'torus-t':
                # THROUGHPUT-BASED ----------------
                # sort the dataset based on latencies
                df_subset = df_subset.sort_values(by='throughput', ascending=False)              
                        
            for index, y in df_subset.iterrows():
                if y['src_region'] in regioni_usate and y['src_region'] != prev_region:
                    continue
                if y['dst_region'] in regioni_usate and y['dst_region'] != prev_region:
                    continue
            
                # Take the first row
                # print("Next Row : ", y)
                print(y['dst_region'])
                print(y['src_region'])
            
                # Update the grid and the dataframe
                if y['src_region'] == prev_region:
                    grid[row][col] = y['dst_region']
                    regioni_usate.append(y['dst_region'])
                    if col == columns-1:
                        last_on_the_row = y['dst_region']                    
                        first_on_the_row = grid[row][0]                       

                        # Find in the dataset the row where src_region is equal to last_on_the_row or first_on_the_row
                        # and dst_region is equal to whichever of the two values is not in src_region
                        yy = df_copy[((df_copy['src_region'] == last_on_the_row) | (df_copy['src_region'] == first_on_the_row)) & ((df_copy['dst_region'] == last_on_the_row) | (df_copy['dst_region'] == first_on_the_row))]
                        # print(yy)
                        df = pd.concat([df,yy], ignore_index=True)

                    df = pd.concat([df, y.to_frame().T], ignore_index=True)
                        
                    print("Grid : ", grid)
                    print("Region used: ", regioni_usate)             
                    print(df)   
                    break
                else:
                    grid[row][col] = y['src_region']
                    regioni_usate.append(y['src_region'])
                    if col == columns-1:
                        last_on_the_row = y['src_region']                    
                        first_on_the_row = grid[row][0]                       

                        # Find in the dataset the rows where src_region is equal to last_on_the_row or first_on_the_row
                        # and dst_region is different from the one in src_region
                        yy = df_copy[((df_copy['src_region'] == last_on_the_row) | (df_copy['src_region'] == first_on_the_row)) & ((df_copy['dst_region'] != last_on_the_row) & (df_copy['dst_region'] != first_on_the_row))]
                        # print(yy)
                        df = pd.concat([df, yy], ignore_index=True)

                    df = pd.concat([df, y.to_frame().T], ignore_index=True)
                        
                    print("Grid : ", grid)
                    print("Region used: ", regioni_usate)                
                    break            
                
                # time.sleep(40)
                        
                # df = pd.concat([df, y], ignore_index=True)
                # df = df.append(next_row)   
                
    print(df)
    return df

def create_fat_tree_topology(df, mode):    
    df_copy = df.copy()
    df = pd.DataFrame()
    
    df_copy[['src_region', 'dst_region']] = df_copy[['src_region', 'dst_region']].astype(str)
    
    # Take unique regions in the dataset
    unique_regions = df_copy['src_region'].unique()    
        
    # For each unique region, 
        # Calculate the sum of latencies and throughput associated with it (both when the region is in src and dst)
        # Sort the regions based on lower latency and higher throughput         
    region_data = []
    for region in unique_regions:
        region_df = df_copy[(df_copy['src_region'] == region) | (df_copy['dst_region'] == region)]
        latency_sum = region_df['latency'].sum()
        throughput_sum = region_df['throughput'].sum()
        region_data.append({'Region': region, 'Latency': latency_sum, 'Throughput': throughput_sum})

    # Sort regions based on lower latency and higher throughput
    
    if mode == 'fat-tree-l':
        # LATENCY-BASED ------------------        
        region_data = sorted(region_data, key=lambda x: (x['Latency'], -x['Throughput']))
        # region_data = sorted(region_data, key=lambda x: (-x['Throughput'], x['Latency']))    
        # print("Ordered regions: ", region_data)
        # print()
    elif mode == 'fat-tree-t':
        # THROUGHPUT-BASED ----------------
        # region_data = sorted(region_data, key=lambda x: (x['Latency'], -x['Throughput']))
        region_data = sorted(region_data, key=lambda x: (-x['Throughput'], x['Latency']))    
        # print("Ordered regions: ", region_data)
        # print()
        
    region_data_to_use_after = region_data
        
    # Switch hierarchy
        # Level 1 -> 20% of regions (out of 10 = 2)
        # Level 2 -> 30% of regions (out of 10 = 5)         
    levels = [0.2, 0.5]
    total_regions = len(unique_regions)
    # Round down the level sizes
    level_sizes = [math.floor(total_regions * level) for level in levels]
    # print("Level sizes: ", level_sizes)
    
    for i in range(len(level_sizes)):
        if i + 1 < len(level_sizes):
            first_regions_to_consider = []            
            second_regions_to_consider = []            
            # print("region data after: ", region_data)

            # Take the corresponding number (i+1) of elements from region_data 
            # for the key "Region" and add them to regions_to_consider
            elements_to_consider = level_sizes[i]
            first_elements = region_data[:elements_to_consider]
            for element in first_elements:
                first_regions_to_consider.append(element['Region'])                   

            # Remove original elements from the dictionary
            region_data = [element for element in region_data if element['Region'] not in first_regions_to_consider]            
            # print("Level 1 region to consider: ", regions_to_consider)
            # print("region data after: ", region_data)
            print("Switch(es) region(s) at Level 1 : ", first_regions_to_consider)
            
            # print(df_copy[~((df_copy['src_region'].isin(regions_to_consider)) & (df_copy['dst_region'].isin(regions_to_consider)))])
            # df_copy = df_copy[~((df_copy['src_region'].isin(regions_to_consider)) & (df_copy['dst_region'].isin(regions_to_consider)))]
            # print(df_copy)

            # Take the corresponding number (i+1) of elements from region_data
            # for the key "Region" and add them to regions_to_consider
            elements_to_consider = level_sizes[i+1]
            second_elements = region_data[:elements_to_consider]
            for element in second_elements:
                second_regions_to_consider.append(element['Region'])

            # Remove original elements from the dictionary
            # region_data = [element for element in region_data if element['Region'] not in regions_to_consider]            
            # print("Level 2 region to consider: ", regions_to_consider)
            # print("region data after: ", region_data)
            print("Switch(es) region(s) at Level 2 : ", second_regions_to_consider)
            
            regions_set = first_regions_to_consider + second_regions_to_consider
            
            # print(df_copy[~((df_copy['src_region'].isin(regions_to_consider[i+2:])) & (df_copy['dst_region'].isin(regions_to_consider[i+2:])))])
            # df_copy = df_copy[~((df_copy['src_region'].isin(regions_to_consider[i+2:])) & (df_copy['dst_region'].isin(regions_to_consider[i+2:])))]
                    
            # Filter rows of the copied DataFrame
            # print(df_copy[df_copy['src_region'].isin(regions_to_consider) & df_copy['dst_region'].isin(regions_to_consider)])
            df_attempt = df_copy[df_copy['src_region'].isin(regions_set) & df_copy['dst_region'].isin(regions_set)]                        
            # print(df_attempt)
            # print(df_copy[~((df_copy['src_region'].isin(regions_to_consider[:i+1])) & (df_copy['dst_region'].isin(regions_to_consider[:i+1])))])
            
            # Remove links within the same level
            df_attempt = df_attempt[~((df_attempt['src_region'].isin(first_regions_to_consider)) & (df_attempt['dst_region'].isin(first_regions_to_consider)))]
            # print(df_attempt)
            # print(df_copy[~((df_copy['src_region'].isin(regions_to_consider[i+2:])) & (df_copy['dst_region'].isin(regions_to_consider[i+2:])))])
            df_attempt = df_attempt[~((df_attempt['src_region'].isin(second_regions_to_consider)) & (df_attempt['dst_region'].isin(second_regions_to_consider)))]
            # print(df_attempt)
            
            links_second_regions_to_consider = second_regions_to_consider.copy()
                        
            random.seed(443)
                                    
            for region in first_regions_to_consider:
                df_reduced = df_attempt[(df_attempt['src_region'] == region) | (df_attempt['dst_region'] == region)]
                            
                random_region = random.choice(links_second_regions_to_consider)
                df_reduced = df_reduced[~((df_reduced['src_region'] == random_region) | (df_reduced['dst_region'] == random_region))]
                links_second_regions_to_consider.remove(random_region)
                
                # if mode == 'fat-tree-l':
                #     # LATENCY-BASED ------------------        
                #     # ordino il dataset in base alle latenze
                #     df_reduced = df_reduced.sort_values(by='latency', ascending=True)
                # elif mode == 'fat-tree-t':
                #     # THROUGHPUT-BASED ----------------
                #     # ordino il dataset in base alle latenze
                #     df_reduced = df_reduced.sort_values(by='throughput', ascending=False)                 
                
                # GESTIRE IL NUMERO DI LINK!!!
                # df_reduced = df_reduced.head(int(0.6 * len(second_regions_to_consider)))
                
                df = pd.concat([df, df_reduced], ignore_index=True)
            
            # rinomino i valori di src e dst aggiungendo alla fine g1 se il valore è in first_regions altrimenti g2
            df['src_region'] = df['src_region'].apply(lambda x: x + '-g1' if x in first_regions_to_consider else x + '-g2')
            df['dst_region'] = df['dst_region'].apply(lambda x: x + '-g1' if x in first_regions_to_consider else x + '-g2')                

    # print(df)        
        
    region_data_to_use_after = [data for data in region_data_to_use_after if data['Region'] not in second_regions_to_consider]
    # print(region_data_to_use_after)
    
    # We only need the last level of the switch hierarchy
    for region in second_regions_to_consider:
        new_link_same_region = {
            'src_region': f'{region}',
            'dst_region': f'{region}-g2',
            'hops': 1,
            'latency': 1,
            'throughput': 0  # setto il throughput con 0 perchè è ininfluente sulla costruzione della topologia
        }
        new_link_df = pd.DataFrame([new_link_same_region])
        df = pd.concat([df, new_link_df], ignore_index=True)

        if mode == 'fat-tree-l':
            # LATENCY-BASED ------------------        
            region_data_to_use_after = sorted(region_data_to_use_after, key=lambda x: (x['Latency'], -x['Throughput']))
            # region_data = sorted(region_data, key=lambda x: (-x['Throughput'], x['Latency']))    
            # print("Regioni ordinate: ", region_data)
            # print()
        elif mode == 'fat-tree-t':
            # THROUGHPUT-BASED ----------------
            region_data_to_use_after = sorted(region_data_to_use_after, key=lambda x: (-x['Throughput'], x['Latency']))
        
        # Take the first value at the 'Region' entry
        other_region = region_data_to_use_after[0]['Region']

        # Remove from region_data
        region_data_to_use_after = [data for data in region_data_to_use_after if data['Region'] != other_region]
                        
        new_link_other_region = {
            'src_region': f'{other_region}',
            'dst_region': f'{region}-g2',
            'hops': 1,
            'latency': df_copy.loc[((df_copy['src_region'] == region) & (df_copy['dst_region'] == other_region)) | ((df_copy['src_region'] == other_region) & (df_copy['dst_region'] == region)), 'latency'].values[0],
            'throughput': df_copy.loc[((df_copy['src_region'] == region) & (df_copy['dst_region'] == other_region)) | ((df_copy['src_region'] == other_region) & (df_copy['dst_region'] == region)), 'throughput'].values[0]
        }
        new_link_df = pd.DataFrame([new_link_other_region])
        df = pd.concat([df, new_link_df], ignore_index=True)

    print(df)        
                                        
    return first_regions_to_consider, second_regions_to_consider, df

def create_double_topology(df, mode):    
    df_copy = df.copy()
    df = pd.DataFrame()    

    # unique_regions = df_copy['src_region'].unique()
        
    if mode == 'double-l':
        # Sort the dataset based on latencies
        df_copy = df_copy.sort_values(by='latency', ascending=False)
    else:
        # double-s
        # Sort the dataset based on latencies
        df_copy = df_copy.sort_values(by='latency', ascending=True)
        
    # Take the first row
    df_row = df_copy.iloc[0]
    src_region = df_row['src_region']
    dst_region = df_row['dst_region']
    
    regions = [src_region, dst_region]
        
    df = pd.concat([df, df_row.to_frame().T], ignore_index=True)
    # df = df.append(df_row)
    print(df)

    return df, regions
    
def abbreviate_regions(input_string):
    output_string = input_string.replace("south", "s")
    output_string = output_string.replace("north", "n")
    output_string = output_string.replace("east", "e")
    output_string = output_string.replace("west", "w")
    return output_string

def region_fix(input_string):
    # Split the string based on hyphens
    parts = input_string.split('-')

    # Map for directions
    directions = {
        's': 'south',
        'n': 'north',
        'e': 'east',
        'w': 'west'
    }

    # Select only the part containing the direction
    direction_part = parts[1]

    # Replace each direction abbreviation with the corresponding full extension
    for abbrev, full_direction in directions.items():
        direction_part = direction_part.replace(abbrev, full_direction)

    # Assemble the string back together
    output_string = '-'.join([parts[0], direction_part, parts[2]])

    return output_string

def check_secondaries(value):
    value = int(value)
    if value < 1:
        raise argparse.ArgumentTypeError("The secondaries value must be an integer greater than or equal to 1.")
    return value

def check_nodes(value):
    value = int(value)
    if value < 1:
        raise argparse.ArgumentTypeError("The nodes value must be greater than 0")
    return value

def check_bandwidth(value):
    value = float(value)
    if value > 10 and value < 0.001:
        raise argparse.ArgumentTypeError("The bandwidth value must be a float between 0.001 and 10.")
    return value

def check_type(value):
    if value not in ["full-mesh", "scale-free-t", "scale-free-l", "scale-free-r", "double-l", "double-s", "torus-l", "torus-t", "torus-r", "fat-tree-t", "fat-tree-l"]:
        raise argparse.ArgumentTypeError('Accepted values are: "full-mesh", "scale-free-t", "scale-free-l", "scale-free-r", "double-l", "double-s", "torus-l", "torus-t", "torus-r", "fat-tree-t", "fat-tree-l"')
    return value

def check_strategy(value):
    if value not in ["latency", "hop"]:
        raise argparse.ArgumentTypeError('Accepted values are: "latency", "hop"')
    return value

def check_dataset(value):
    if value not in ["our", "diablo"]:
        raise argparse.ArgumentTypeError('Accepted values are: "our", "diablo"')
    return value

def check_dynamic(value):
    value = int(value)
    if value not in [0, 1, 2, 3, 4]:
        raise argparse.ArgumentTypeError("The dynamic value must be either 0, 1, 2, 3, or 4.")
    return value

def check_blockchain(value):
    if value not in ["algorand", "poa", "quorum", "diem", "solana"]:
        raise argparse.ArgumentTypeError('Accepted values are: "algorand" "poa" "quorum" "diem" "solana"')
    return value

def check_switch(value):
    value = int(value)
    if value < 2 :
        raise argparse.ArgumentTypeError("The number of switches should be greater than 1.")
    return value

def check_latency(value):
    value = int(value)
    if value < 1:
        raise argparse.ArgumentTypeError("The latency between switch shoudl be greater than 0.")
    return value

# --------------------------------------------- ARGS DEFAULT
parser = argparse.ArgumentParser(description='Script with optional arguments.')
parser.add_argument('--secondaries', type=check_secondaries, default=10, help='Secondaries value (integer greater than or equal to 1)')
parser.add_argument('--nodes', type=check_nodes, default=1, help='Nodes value (integer greater or equal than 1)')
parser.add_argument('--bandwidth', type=check_bandwidth, default=1, help='Bandwidth value on switch (float between 0.001 and 10)')
parser.add_argument('--type', type=check_type, default='full-mesh', help="Type value ('full-mesh', 'scale-free-t', 'scale-free-l', 'scale-free-r', 'torus-l', 'torus-r', 'torus-t', 'fat-tree-t', 'fat-tree-l').")
parser.add_argument('--strategy', type=check_strategy, default='hop', help="Strategy value ('latency', 'hop').")
parser.add_argument('--dataset', type=check_dataset, default='diablo', help="Dataset value ('our', 'diablo').")
parser.add_argument('--dynamic', type=check_dynamic, default='0', help="Dynamic value (either 0:no, 1:packet_drop, 2:congestion, 3:switch-leave, 4:crash).")
parser.add_argument('--blockchain', type=check_blockchain, default='poa', help="Blockchain to use ('algorand' 'poa' 'quorum' 'diem' 'solana').")
parser.add_argument('--switch', type=check_switch, default='250', help="Number of switches in the topology (integer greater or equal than 2).")
parser.add_argument('--latency', type=check_latency, default='100', help="Latency between switches (integer greater than 0).")

args = parser.parse_args()

secondaries = args.secondaries
nodes_per_region = args.nodes
mode = args.type
bandwidth = args.bandwidth

bandwidth = int(bandwidth * 1024)

strategy = args.strategy
dataset = args.dataset
blockchain = args.blockchain

switches = args.switch
# switch_latency = int(args.latency/2)
switch_latency = int(args.latency)
switch_throughput = 1
data = []
for i in range(1, switches + 1):
    for j in range(i + 1, switches + 1):
        data.append((i, j, switch_latency, switch_throughput))
topo_data = pd.DataFrame(data, columns=['src_region', 'dst_region', 'latency', 'throughput'])        
# print(topo_data)

dynamic = args.dynamic
if dynamic > 0 and 'double' in mode:
    print("You cannot execute dynamics with double-region topology")
    sys.exit(1)  # Exit with error code 1

aws_data = pd.read_csv(f"misc/{dataset}-aws.csv")
# bw_data = pd.read_csv("misc/bw-df.csv")
output="kollaps/examples/topology.xml"
file_xml_basic='misc/sample-topology.xml'

tree = ET.parse(file_xml_basic)
root = tree.getroot()

aws_data['src_region'] = aws_data['src_region'].map(abbreviate_regions)
aws_data['dst_region'] = aws_data['dst_region'].map(abbreviate_regions)

if "double" in mode:
    aws_data, regions = create_double_topology(aws_data, mode)
else:
    regions = ['af-south-1', 'ap-northeast-1', 'ap-south-1', 'ap-southeast-2', 'eu-north-1', 'eu-south-1', 'me-south-1', 'sa-east-1', 'us-east-2', 'us-west-2']   

regions = [abbreviate_regions(region) for region in regions]
# nodes_per_region = int(nodes / len(regions))

# --------------------------------------------- 
# Node endpoint layer
# Add blockchain nodes

chain_nodes = []
for region in regions:
    
    bridge = ET.SubElement(root.find(".//bridges"), "bridge", name=f'{region}')
    bridge.tail = '\n'
    
    for i in range(nodes_per_region):    
        chain_nodes.append(f'{region}-n{i+1}') 
        service = ET.SubElement(root.find(".//services"), "service", name=f'{region}-n{i+1}', image=f"kollaps/entity:1.0")
        service.tail = "\n"
        
        # bandwidth = bw_data.loc[bw_data['region'] == region, 'bandwidth'].iloc[0]              
        # link = ET.SubElement(root.find(".//links"), "link", origin=f'{region}-in', dest=f'{region}-n{i+1}', latency='0.001', upload=f'{bandwidth}Gbps', download=f'{bandwidth}Gbps', network="kollaps_network")
        # link.tail = "\n" 
        # link = ET.SubElement(root.find(".//links"), "link", origin=f'{region}-n{i+1}', dest=f'{region}', latency='3.001', upload=f'{bandwidth}Mbps', download=f'{bandwidth}Mbps', network="kollaps_network")
        link = ET.SubElement(root.find(".//links"), "link", origin=f'{region}-n{i+1}', dest=f'{region}', latency='3.001', upload=f'1Gbps', download=f'1Gbps', network="kollaps_network")
        link.tail = "\n" 
        # if nodes_per_region > 1:
        #     link = ET.SubElement(root.find(".//links"), "link", origin=f'{region}-n{i+1}', dest=f'{region}', latency='0.001', upload=f'{bandwidth}Gbps', download=f'{bandwidth}Gbps', network="kollaps_network")
        #     link.tail = "\n"     
                
        # link = ET.SubElement(root.find(".//links"), "link", origin=f'{region}-n{i+1}', dest='nodes-gate-out', latency='0.001', upload=f'{bandwidth}Gbps', network="kollaps_network")
        # link.tail = "\n" 
        # link = ET.SubElement(root.find(".//links"), "link", origin='nodes-gate-in', dest=f'{region}-n{i+1}', latency='0.001', upload=f'{bandwidth}Gbps', network="kollaps_network")
        # link.tail = "\n" 
        
        schedule = ET.SubElement(root.find(".//dynamic"), "schedule", name=f'{region}-n{i+1}', time='0.0', action='join')
        schedule.tail = '\n'

# --------------------------------------------- 
# Secondary layer
# Add secondary(s)
# bridge = ET.SubElement(root.find(".//bridges"), "bridge", name='secondaries-gate')
# bridge.tail = '\n'

for i in range(secondaries):
    chain_nodes.append(f'secondary-{i+1}')
    service = ET.SubElement(root.find(".//services"), "service", name=f'secondary-{i+1}', image="kollaps/entity:1.0")
    service.tail = "\n"
    
    # link = ET.SubElement(root.find(".//links"), "link", origin=f'secondary-{i+1}', dest='nodes-gate-in', latency='0.001', upload='10Gbps', network="kollaps_network")
    # link.tail = "\n" 
    # link = ET.SubElement(root.find(".//links"), "link", origin='nodes-gate-out', dest=f'secondary-{i+1}', latency='0.001', upload='10Gbps', network="kollaps_network")
    # link.tail = "\n" 
    
    # link = ET.SubElement(root.find(".//links"), "link", origin=f'secondary-{i+1}', dest='primary', latency='0.001', upload='1Gbps', download='1Gbps', network="kollaps_network")
    # link.tail = "\n" 
        
    schedule = ET.SubElement(root.find(".//dynamic"), "schedule", name=f'secondary-{i+1}', time='0.0', action='join')
    schedule.tail = '\n' 
    
# --------------------------------------------- 
# Primary layer
# Add primary
service = ET.SubElement(root.find(".//services"), "service", name='primary', image="kollaps/primary:1.0")
service.set("command", str(chain_nodes))
service.tail = "\n"

# link = ET.SubElement(root.find(".//links"), "link", origin='primary', dest='secondaries-gate', latency='0.001', upload='10Gbps', download='10Gbps', network="kollaps_network")
# link = ET.SubElement(root.find(".//links"), "link", origin='primary', dest='secondaries-gate', latency='0.001', upload='10Gbps', download='10Gbps', network="kollaps_network")
# link.tail = "\n" 

schedule = ET.SubElement(root.find(".//dynamic"), "schedule", name=f'primary', time='0.0', action='join')
schedule.tail = '\n'
        
# --------------------------------------------- 
# AWS layer
# Add bridges, regions, hops

# for region in regions:
#     # bridge = ET.SubElement(root.find(".//bridges"), "bridge", name=f'{region}-in')
#     # bridge.tail = '\n'
#     # bridge = ET.SubElement(root.find(".//bridges"), "bridge", name=f'{region}-out')
#     # bridge.tail = '\n'
#     bridge = ET.SubElement(root.find(".//bridges"), "bridge", name=f'{region}')
#     bridge.tail = '\n'    
    
#     # for i in range(secondaries):
#     #     link = ET.SubElement(root.find(".//links"), "link", origin=f'{region}', dest=f'secondary-{i+1}', latency='0.001', upload='10Gbps', download='10Gbps', network="kollaps_network")
#     #     link.tail = "\n" 

# if len(regions) > 1:    
    
# sum_bridges = aws_data['hops'].sum()        
# CONSTRUCT THE LINK
# Section code to have at least 1 region for each region in the src column
if "double" not in mode:
    unique_regions = aws_data['src_region'].unique()
    # print(unique_regions)            
    for region in regions:
        # print(aws_data[aws_data['dst_region'] == region])
        # print(aws_data['dst_region'])
        # print(unique_regions)
        if region not in unique_regions:
            row_index = aws_data[aws_data['dst_region'] == region].index[0]
            # Scambia i valori di col1 e col2 nella riga trovata
            aws_data.at[row_index, 'src_region'], aws_data.at[row_index, 'dst_region'] = aws_data.at[row_index, 'dst_region'], aws_data.at[row_index, 'src_region']

    # Filter in the dataframe where there are the regions
    aws_data = aws_data[aws_data['src_region'].isin(regions) | aws_data['dst_region'].isin(regions)]
    
    unique_regions = aws_data['src_region'].unique()
    # print(unique_regions)    

if "double" not in mode:
    unique_switches = topo_data['src_region'].unique()
    for i in range(1, switches+1):
        # print(aws_data[aws_data['dst_region'] == region])
        # print(aws_data['dst_region'])
        # print(unique_regions)
        if i not in unique_switches:
            row_index = topo_data[topo_data['dst_region'] == i].index[0]
            # Scambia i valori di col1 e col2 nella riga trovata
            topo_data.at[row_index, 'src_region'], topo_data.at[row_index, 'dst_region'] = topo_data.at[row_index, 'dst_region'], topo_data.at[row_index, 'src_region']
    
    unique_switches = topo_data['src_region'].unique()
    # print(unique_switches)   


# print()
# print("AWS : before")
# print(aws_data.shape[0])
if 'full-mesh' in mode:
    topo_data = create_full_mesh_topology(topo_data)
elif 'scale-free' in mode:
    topo_data = create_scale_free_topology(topo_data, mode)
    # in create_scale_free_topology uso unique_region. se dopo qui ri-uso devo sistemare
    
    topo_data.to_csv("misc/logs/topo_data_tmp.csv", index=False)
    topo_data.to_csv(f"results/img/topo_data_{switches}_tmp.csv", index=False)
elif 'torus' in mode:
    topo_data = create_torus_topology(topo_data, mode)
elif 'fat-tree' in mode:
    first_gate_regions, last_gate_regions, topo_data = create_fat_tree_topology(topo_data, mode)
    for region in first_gate_regions:        
        bridge = ET.SubElement(root.find(".//bridges"), "bridge", name=f'{region}-g1')
        bridge.tail = '\n'  
    for region in last_gate_regions:        
        bridge = ET.SubElement(root.find(".//bridges"), "bridge", name=f'{region}-g2')
        bridge.tail = '\n'        
# elif 'hypercube' in mode:
#     topo_data = create_hypercube_topology(topo_data)
# print()
# print("AWS : after")
print(f"{mode} with links number: ", topo_data.shape[0])
# print(topo_data)
    
# upload_bandwidth = bandwidth * nodes_per_region
# upload_bandwidth = max(10, upload_bandwidth)
# Conversione da GBps a MBps
# upload_bandwidth = bandwidth * nodes_per_region * len(regions)
upload_bandwidth = bandwidth
# upload_bandwidth = max(10, upload_bandwidth)
# Conversione da GBps a MBps

# download_bandwidth = bw_data.loc[bw_data['region'].str.contains(dest)].sort_values(by=lambda x: len(x), ascending=False)['bandwidth'].iloc[0]
# download_bandwidth = bandwidth * nodes_per_region * len(regions)
download_bandwidth = bandwidth
# download_bandwidth = max(10, download_bandwidth)

for index, row in topo_data.iterrows():    
    origin = row['src_region']    
    dest = row['dst_region']
    latency = row['latency']    
    
    link = ET.SubElement(root.find(".//links"), "link") 
    link.set("origin", f's{origin}')
    link.set("dest", f's{dest}')
    link.set("latency", f'{latency}')               
    # link.set("latency", '0.001')                   
    link.set("upload", f'{upload_bandwidth}Mbps')
    link.set("download", f'{download_bandwidth}Mbps')
    link.set("network", "kollaps_network")
    link.tail = "\n"

for i in range(1, switches+1):
    bridge = ET.SubElement(root.find(".//bridges"), "bridge", name=f's{i}')
    bridge.tail = '\n'  

# ---------------------------------------------     
# Random attachment of region to switches in the topology
unique_switches = pd.concat([topo_data['src_region'], topo_data['dst_region']]).value_counts()
print(unique_switches)
unique_switches_list = unique_switches.index.tolist()
random.seed(443)
random.shuffle(unique_switches_list)
random.seed(80)
random.shuffle(unique_switches_list)

# unique_switches_sorted = unique_switches.sort_values(ascending=True)
# unique_switches_list = unique_switches_sorted.index.tolist()
# if 'scale-free' not in mode:
#     random.seed(443)
#     random.shuffle(unique_switches_list)
# else:
#     switch_high_degree_to_remove = int(len(unique_switches_list) * 0.30)
#     unique_switches_list = unique_switches_list[:-switch_high_degree_to_remove]        
    
for region in unique_regions:
    head_switch = unique_switches_list.pop(0)
    # print(head_switch)
    link = ET.SubElement(root.find(".//links"), "link") 
    link.set("origin", f'{region}')
    link.set("dest", f's{head_switch}')
    # link.set("latency", f'{switch_latency}')               
    link.set("latency", f'0.001')  
    link.set("upload", f'{upload_bandwidth}Mbps')
    link.set("download", f'{download_bandwidth}Mbps')
    link.set("network", "kollaps_network")
    link.tail = "\n"    
    unique_switches_list.append(head_switch)

    # new_row = pd.DataFrame([[region, head_switch, 0.001, 1]], columns=['src_region', 'dst_region', 'latency', 'throughput'])
    # topo_data = pd.concat([topo_data, new_row], ignore_index=True)    

# ---------------------------------------------     
# Dynamic section - crash on bridge
if dynamic > 0:
    dynamic_regions = int(len(regions) * 0.2)    

    # Random selection of regions
    random.seed(443)
    random_regions_selection = random.sample(regions, dynamic_regions)
    # print(random_regions_selection)
        
    # Random selection of links
    links = root.findall('.//links/link')
    links = [link for link in links if re.match(r'^s\d+', link.attrib['origin']) and re.match(r'^s\d+', link.attrib['dest'])]
    # links = [link for link in links if link.attrib['origin'].startswith('s') and not(link.attrib['origin'].startswith('sa')) and link.attrib['dest'].startswith('s') and not(link.attrib['dest'].startswith('sa'))]    
    random.seed(443)
    selected_links = random.sample(links, int(len(links)/3))
        
    #deploy time + workload_prep_time + workload_time/3 . ANNULLO-CHECK-LATENCY
    if blockchain == "algorand": #(11*60=~700)+(100)+(276/3=100)=950 
        # dynamic_start = 1250.0 
        dynamic_start = 600.0 
    elif blockchain == "poa": #(7*60=~500)+(100)+(276/3=140)=750
        # dynamic_start = 1100.0
        dynamic_start = 540.0
    elif blockchain == "quorum": #(7*60=~500)+(100)+(276/3=140)=750
        # dynamic_start = 1100.0 
        dynamic_start = 540.0 
    elif blockchain == "diem": #(38*60=~2300)+(100)+(276/3=140)=2650
        # dynamic_start = 3100.0
        dynamic_start = 2650.0
    elif blockchain == "solana": #(30/35*60=~2100)+(100)+(276/3=140)=2550
        # dynamic_start = 2550.0
        dynamic_start = 2050.0
        
    # ripristino i nodi 
    join_time_after_crash = dynamic_start + 60.0        

    if dynamic == 1: #packet_drop        
        for link in selected_links:
            origin=link.attrib['origin']
            dest=link.attrib['dest']
            schedule = ET.SubElement(root.find(".//dynamic"), "schedule", origin=f'{origin}', dest=f'{dest}', time=f'{dynamic_start}', drop='1.0')
            schedule.tail = '\n'                            
        
        # for region in random_regions_selection:    
        #     for elem in root.iter('link'):
        #         if elem.get('origin') == region:
        #             dest = elem.get('dest')
        #             schedule = ET.SubElement(root.find(".//dynamic"), "schedule", origin=f'{region}', dest=f'{dest}', time=f'{dynamic_start}', drop='0.4')
        #             schedule.tail = '\n'    
                    
        #             schedule = ET.SubElement(root.find(".//dynamic"), "schedule", origin=f'{region}', dest=f'{dest}', time=f'{join_time_after_crash}', drop='0')
        #             schedule.tail = '\n'
    elif dynamic == 2: #congestion        
        for link in selected_links:
            origin=link.attrib['origin']
            dest=link.attrib['dest']
            schedule = ET.SubElement(root.find(".//dynamic"), "schedule", origin=f'{origin}', dest=f'{dest}', time=f'{dynamic_start}', upload=f'{int(upload_bandwidth *0.2)}Mbps', download=f'{int(download_bandwidth *0.2)}Mbps')
            schedule.tail = '\n'          
        
        # for region in random_regions_selection:    
        #     for elem in root.iter('link'):
        #         if elem.get('origin') == region:
        #             dest = elem.get('dest')              
        #             schedule = ET.SubElement(root.find(".//dynamic"), "schedule", origin=f'{region}', dest=f'{dest}', time=f'{dynamic_start}', upload=f'{int(upload_bandwidth *0.2)}Mbps', download=f'{int(download_bandwidth *0.2)}Mbps')
        #             schedule.tail = '\n'            
                    
        #             schedule = ET.SubElement(root.find(".//dynamic"), "schedule", origin=f'{region}', dest=f'{dest}', time=f'{join_time_after_crash}', upload=f'{int(upload_bandwidth)}Mbps', download=f'{int(download_bandwidth)}Mbps')
        #             schedule.tail = '\n'                                
    elif dynamic == 3: #switch-leave            
        for region in random_regions_selection:                    
                schedule = ET.SubElement(root.find(".//dynamic"), "schedule", name=f'{region}', time=f'{dynamic_start}', action='leave')
                schedule.tail = '\n'
    elif dynamic == 4: #crash                    
        for region in random_regions_selection:            
            for i in range(nodes_per_region):          
            
                schedule = ET.SubElement(root.find(".//dynamic"), "schedule", name=f'{region}-n{i+1}', time=f'{dynamic_start}', action='crash')
                # schedule = ET.SubElement(root.find(".//dynamic"), "schedule", name=f'{region}', time=f'{dynamic_start}', action='leave')
                schedule.tail = '\n'

                schedule = ET.SubElement(root.find(".//dynamic"), "schedule", name=f'{region}-n{i+1}', time=f'{join_time_after_crash}', action='join')
                schedule.tail = '\n'
            
# ---------------------------------------------     
# Strategy insertion
config_property = ET.SubElement(root.find(".//config"), "property", shortest_path=f'{strategy}')
config_property.tail = "\n"

# ---------------------------------------------     
tree.write(output)
# aws_data.to_csv("misc/logs/aws_data_tmp.csv", index=False)

avg_latency = topo_data['latency'].mean()
print("Avg latency:", avg_latency)


# Topo-Plot context-------------------------------------------
# # topo_data['src_region'] = topo_data['src_region'].apply(region_fix)
# # topo_data['dst_region'] = topo_data['dst_region'].apply(region_fix)
# # for region in regions:
# #     region_fix(region)

# topo_data = topo_data.sort_values(by='latency')

# # Graph creation
# G = nx.from_pandas_edgelist(topo_data, source='src_region', target='dst_region', edge_attr=True, create_using=nx.DiGraph)

# plt.figure(figsize=(21, 16))

# # ordered Layout
# pos = nx.circular_layout(G)
# # pos = nx.nx_agraph.graphviz_layout(G, prog="twopi", root=0)

# edge_labels = {(src, dst): {'latency': topo_data[(topo_data['src_region'] == src) & (topo_data['dst_region'] == dst)]['latency'].values[0],
#                             'throughput': topo_data[(topo_data['src_region'] == src) & (topo_data['dst_region'] == dst)]['throughput'].values[0]}
#                for src, dst in G.edges()}

# # edge_width = [1 / d['latency'] for _, _, d in G.edges(data=True)]
# edge_width = 2

# # Node draw
# nx.draw_networkx_nodes(G, pos, node_size=15000, node_color='#DCDCDC')  # Grigio molto chiaro

# # Labels draw
# nx.draw_networkx_labels(G, pos, font_color='black', font_size=23)  # Font nero e ingrandito

# # Disegna archi con attributi
# for (u, v, d) in G.edges(data=True):
#     # Edges draw
#     nx.draw_networkx_edges(G, pos, width=edge_width, alpha=0.7, edge_color='black', arrows=True, arrowstyle='-|>')

#     # Calcola la posizione dei puntini degli hops
#     # num_hops = d['hops']
#     # for i in range(1, num_hops + 1):
#     #     hop_pos = (pos[u][0] * (1 - i / (num_hops + 1)) + pos[v][0] * (i / (num_hops + 1)),
#     #                pos[u][1] * (1 - i / (num_hops + 1)) + pos[v][1] * (i / (num_hops + 1)))
#         # plt.plot(*hop_pos, 'o', color='lightgrey', markersize=10)

#     # Aggiungi etichette di throughput con offset
#     # offset = 0.35 # Offset for centered label
#     x = (pos[u][0] + pos[v][0]) / 2
#     y = (pos[u][1] + pos[v][1]) / 2
#     angle = math.atan2(pos[v][1] - pos[u][1], pos[v][0] - pos[u][0]) * 180 / math.pi
#     # print(angle)
#     # angle = 135
#     if angle > 90:
#         angle -= 180
#     # if d["throughput"] > 100:
#     # plt.text(x, y, f'{d["throughput"]} MB/s', horizontalalignment='center', verticalalignment='center', rotation=angle, fontsize=15, rotation_mode='anchor', color='black')

# # plt.title(f"{mode}", fontsize=35)
# plt.axis('off')
# plt.savefig(f'results/img/{mode}_v2_network_graph.png', format='png', bbox_inches='tight')
# plt.savefig(f'results/img/{mode}_v2_network_graph.pdf', dpi=500, bbox_inches='tight')

print("Number of links: ", topo_data.shape[0])

edges = list(zip(topo_data['src_region'], topo_data['dst_region']))
G = nx.Graph()
G.add_edges_from(edges)
plt.figure(figsize=(30, 22))
pos = nx.fruchterman_reingold_layout(G)
edge_width = 0.05
nx.draw(G, pos, node_size=150, node_color='black')
nx.draw_networkx_edges(G, pos, width=edge_width, alpha=0.6, edge_color='black', arrows=True, arrowstyle='-|>')    

# plt.title("Scale-Free Network")  
plt.tight_layout()      
plt.savefig(f"results/img/{mode}_{switches}_network_graph.png")
plt.savefig(f'results/img/{mode}_{switches}_network_graph.pdf', dpi=500, bbox_inches='tight')        