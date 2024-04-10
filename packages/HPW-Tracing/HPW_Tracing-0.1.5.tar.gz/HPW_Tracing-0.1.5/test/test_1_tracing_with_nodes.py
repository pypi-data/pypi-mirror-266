from HPW_Tracing import tracing_with_node,  tracing_with_link, tracing_between_nodes, tracing_between_links
from HPW_Tracing import load_graphs

G, G_reverse = load_graphs()

## case 1: tracing with nodeID
nodeID = '5793084'  # use ufid
# nodeID = 'AS019087'  # or yoou can use mh_number
direction = 'upstream'
distance = 1000000  #  put None if you want to search the whole network, it will be much faster rather than defining a large distance
# or else you can choose a distance, for example, 1000 ft

node_dict,edges_df = tracing_with_node(G, nodeID, direction, distance)