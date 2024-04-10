import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict

class Graph():
    def __init__(self):
        self.graph = defaultdict(list)
    def add_edge(self,u,v,w):
        self.graph[u].append((v,w))
        self.graph[v].append((u,w))
    def prims(self):
        MST = []
        visited = set()
        start_vertex = next(iter(self.graph))
        visited.add(start_vertex)
        min_weight = 0

        while len(visited) < len(self.graph):
            min_edge = None
            min_edge_weight = float('inf')
            for u in visited:
                for v,weight in self.graph[u]:
                    if v not in visited and weight < min_edge_weight:
                        min_edge_weight = weight
                        min_edge = (u,v,weight)
            if min_edge:
                MST.append(min_edge)
                visited.add(min_edge[1])
                min_weight += min_edge[2]
        return MST,min_weight
    def draw_graph(self,MST):
        G = nx.Graph()
        for u,v,weight in MST:
            G.add_edge(u,v,weight=weight)
        pos = nx.spring_layout(G)
        nx.draw(G,pos,with_labels = True,node_size = 2000,node_color = 'lightblue')
        labels = nx.get_edge_attributes(G,'weight')
        nx.draw_networkx_edge_labels(G,pos,edge_labels = labels)
        plt.title('Minimum Spanning Tree Using Prims Algorithm')
        plt.show()
g = Graph()
V = int(input("Enter the Number of Vertices:"))
E = int(input("Enter the Number of Edges:"))
for _ in range(E):
    edge = input().split()
    u,v,w = edge[0],edge[1],int(edge[2])
    g.add_edge(u,v,w)
MST,min_weight = g.prims()
print("\n Selected Edges")
for edge in MST:
    print(f"{edge[0]}--{edge[1]}=={edge[2]}")
rejected_edges = set()
for u in g.graph:
    for v,weight in g.graph[u]:
        if v > u and (u,v,weight) not in [e for e in MST]:
            if (u,v,weight) not in rejected_edges:
                rejected_edges.add((u,v,weight))
                print(f"Rejected Edges : {u}--{v} == {weight} (forms cycle)")
print(f"Minimum cost:{min_weight}")
g.draw_graph(MST)
            
                
