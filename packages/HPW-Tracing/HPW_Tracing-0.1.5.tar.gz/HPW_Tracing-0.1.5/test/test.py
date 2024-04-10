from HPW_Tracing.Load_data import load_data
from HPW_Tracing.Build_graphs import iniciate_graph
from HPW_Tracing.Tracing import create_mhNum_UFID_dict, tracing_with_node


db = 'C:\PythonProjects\__db'
datawarehouse_infrastrcuture  = r'C:\Users\C21252\City of Houston\WWIP Planning Data Warehouse - General\GIS Database\01_Infrastructure'
forceupdate = False

G = iniciate_graph(db, datawarehouse_infrastrcuture, forceupdate)

# Case 1 using mh_number
nodeID = 'AS019087'  # tracing starting node
direction = 'upstream'
distance = 1000000

dict = create_mhNum_UFID_dict(db)

node_dict,edges_df = tracing_with_node(G, dict, nodeID, direction, distance)
