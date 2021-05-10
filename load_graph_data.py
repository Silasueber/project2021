import networkx as nx
import pandas as pd
from django_pandas.io import read_frame

import sys
import os
sys.path.append(
    os.path.join(os.path.dirname(__file__), 'project2021')
)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project2021.settings")
import django
django.setup()
from django.conf import settings

from landing.models import TwitterUser,Connections



#get django query set
qs_users = TwitterUser.objects.all()
qs_connections= Connections.objects.all()
#create pd dataframe
df_nodes = read_frame(qs_users)
df_edges = read_frame(qs_connections)
#alternatively, add only special fields to df from query set
#df = read_frame(qs, fieldnames=['age', 'wage', 'full_name'])

#check nodes df
print(df_nodes.head())
print(df_nodes.describe())


#check edges df
print(df_edges.head())
print(df_edges.describe())


#merge nodes and edges df
df_complete = pd.concat([df_nodes,df_edges], axis=1)
print(df_complete.head())

#create a networkx directional graph
G = nx.from_pandas_edgelist(
    df=df_complete,
    source="fromUser", #fieldname of django qs
    target="toUser", #fieldname of django qs
    edge_attr=["amount"], #edge weights from django qs
    create_using=nx.DiGraph #type of graph (here directional)
)

#inspect graph object
print(nx.info(G))
#check if edge metadata is added correctly
print(list(G.edges(data=True))[0:5])


#add node metadata
#nx.set_node_attributes(G, df_nodes["followerCount"], "followerCount")
for node, metadata in df_nodes.set_index("username").iterrows():
    for key, val in metadata.items(): #treat df features as dict
        G.nodes[node][key] = val
print(list(G.nodes(data=True))[0:5])

##test data integrity
def test_graph_integrity(G,num_nodes,num_edges):
    """Test integrity of raw  graph."""
    assert len(G.nodes())==num_nodes
    assert len(G.edges())==num_edges

def test_nodes_metadata(G):
    """Test node metadata."""
    for n, d in G.nodes(data=True):
        assert "followerCount" in d.keys()
        assert d["followerCount"]>=0 

def test_edges_metadata(G):
    """Test edge metadata."""
    for n, d in G.edges(data=True):
        assert "amount" in d.keys()    
        assert d["amount"]>=0 


test_graph_integrity(G,num_nodes=22,num_edges=462)  
test_nodes_metadata(G)

#save graph for future
#filepath=""
#nx.write_gpickle(G, filepath)

##DO SOME AWESOME GRAPH ANALYSIS NEXT

