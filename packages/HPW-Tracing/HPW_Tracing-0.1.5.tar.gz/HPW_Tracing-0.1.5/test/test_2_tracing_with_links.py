from HPW_Tracing import tracing_with_link, load_graphs


G,_ = load_graphs()

linkID  = '1867318'
distance = 10000000  # search withing 1000000 ft,  put None if you want to search the whole network
direction = 'downstream'

node_dict,edges_df = tracing_with_link(G, linkID, direction, distance)