
from HPW_Tracing import load_graphs, tracing_between_nodes

G, reversed_graph = load_graphs()

start_node = '2132847'
end_node = '2132845'

# or you can use mh_number
# start_node = 'AS019037'
# end_node = 'AS019087'


nodes, edges = tracing_between_nodes(G, start_node, end_node)