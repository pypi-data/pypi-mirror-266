from HPW_Tracing import load_graphs, tracing_between_links

G,_ = load_graphs()
start_link = '2509894'
end_link = '2509500'
nodes, edges = tracing_between_links(G, start_link, end_link)