import pickle
import networkx as nx
import pandas as pd
import os
from HPW_Tracing.Load_data import load_data
from HPW_Tracing.Build_graphs.network_correction import correct_network


def iniciate_graph(db_folder: str, datawarehouse: str, update: bool)-> nx.DiGraph:
    # make src folder if it does not exist
    if not os.path.exists(db_folder):
        os.makedirs(db_folder)

    if update:
        print('-' * 50)
        print('Removing the pre-existing pickle files')
        for file in os.listdir(db_folder):
            if file.endswith('.pkl'):
                os.remove(os.path.join(db_folder, file))
        update = False

    if os.path.exists(os.path.join(db_folder, 'network_graph.pkl')):
        print('-' * 50)
        print('Loading the network graph from the pickle file...')
        G = load_graphs_from_pickle(db_folder)
    else:
        print('-' * 50)
        print('Creating the network graph...')
        make_graphs_pickle(db_folder, datawarehouse, update)
        G = load_graphs_from_pickle(db_folder)

    print('-' * 50)
    print('Network graph created successfully.')
    return G


def load_graphs_from_pickle(db_folder: str)-> nx.DiGraph:
    with open(os.path.join(db_folder, 'network_graph.pkl'), 'rb') as handle:
        G = pickle.load(handle)
    return G


def make_graphs_pickle(db_folder: str, datawarehouse: str, update: bool):
    # if the pickle file corrected_network_data.pkl exists, load the corrected network data from the pickle file
    if os.path.exists(os.path.join(db_folder, 'corrected_network_data.pkl')):
        print('-' * 50)
        print('Loading the corrected network data from the pickle file...')
        with open(os.path.join(db_folder, 'corrected_network_data.pkl'), 'rb') as handle:
            corrected_network_data = pickle.load(handle)
    else:
        # load the data
        gm_shp_gdf, fm_shp_gdf, mh_shp_gdf, cleanout_shp_gdf = load_data(db_folder, datawarehouse, update)

        # correct the network data
        corrected_network_data = correct_network(gm_shp_gdf, fm_shp_gdf, mh_shp_gdf, cleanout_shp_gdf, db_folder)

    # # create a directed graph from the sewer network
    G = nx.from_pandas_edgelist(corrected_network_data, 'start_mh', 'end_mh', edge_attr=['UFID', 'type', 'length'],
                                create_using=nx.DiGraph())

    # save G into a pickle file
    with open(os.path.join(db_folder, 'network_graph.pkl'), 'wb') as handle:
        pickle.dump(G, handle, protocol=pickle.HIGHEST_PROTOCOL)

    print ('Graph created successfully and saved to the database folder as network_graph.pkl.')




