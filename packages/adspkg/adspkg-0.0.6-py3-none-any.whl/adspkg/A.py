print(''' 
!pip install scipy
!pip install networkx
!pip install matplotlib

import pandas as pd
import networkx as nx
from matplotlib import pyplot as plt

# Load data
df = pd.read_csv("https://drive.google.com/file/d/1NmsUSXDJx4-bARZqqXtzpYAu6XWn8RCK/view?usp=drive_link", sep=" ", header=None, names=["From", "To"])

# Load edgelist
fb_graph = nx.from_pandas_edgelist(df, source="From", target="To")

print(list(fb_graph.nodes())[:50])

print(list(fb_graph.edges())[:50])

# Convert to undirected graph
G = nx.Graph(fb_graph)

nx.draw(fb_graph, with_labels=False)

print(list(nx.degree(fb_graph))[:25])

nx.degree(fb_graph, 25)

degree_centrality_dict = nx.degree_centrality(fb_graph)
degree_centrality_list = list(degree_centrality_dict.items())[:25]
print(degree_centrality_list)

sorted(nx.degree_centrality(fb_graph).values())
m_influential = nx.degree_centrality(G)
count = 0
for w in sorted(m_influential, key=m_influential.get, reverse=True):
  print(w, m_influential[w])
  count += 1
  if count >= 25:
    break

# Assuming G is your graph
pos = nx.spring_layout(G)  # Corrected function name
betCent = nx.betweenness_centrality(G, normalized=True, endpoints=True)
node_color = [20000.0 * G.degree(v) for v in G]
node_size = [v * 10000 for v in betCent.values()]
plt.figure(figsize=(20, 20))
nx.draw_networkx(G, pos=pos, with_labels=False, node_color=node_color, node_size=node_size)
plt.show()

# Print the top 5 nodes with highest betweenness centrality
top_nodes = sorted(betCent, key=betCent.get, reverse=True)[:5]
print("Top 5 nodes with highest betweenness centrality:", top_nodes)

closeness_centrality = nx.centrality.closeness_centrality(G)
(sorted(closeness_centrality.items(), key = lambda item: item[1], reverse = True))[:8]

node_size = [v * 50 for v in closeness_centrality.values()]
plt.figure(figsize = (15, 8))
nx.draw_networkx(G, pos = pos, node_size = node_size, with_labels = False, width = 0.15)
plt.axis("off")

nx.average_clustering(G)

triangles_per_node = list(nx.triangles(G).values())
sum(triangles_per_node) / 3
# Dividing by 3 because each triangle is counted once for each node

nx.has_bridges(G)

bridges = list(nx.bridges(G))
len(bridges)

local_bridges = list(nx.local_bridges(G, with_span = False))
len(local_bridges)

plt.figure(figsize = (15, 8))
nx.draw_networkx(G, pos = pos, node_size = 10, with_labels = False, width = 0.15)
nx.draw_networkx_edges(G, pos, edgelist = local_bridges, width = 0.5, edge_color = "green")
nx.draw_networkx_edges(G, pos, edgelist = bridges, width = 0.5, edge_color = "blue")
plt.axis("off")

 ''')

    
        

