class Graph:

    def __init__(self, adj_matrix):
        self.adj_matrix = adj_matrix

class MultiGraph(Graph):

    def __init__(self, graph=None, adj_matrix=None):

        if graph is None and adj_matrix is None:
            raise ERROAPROPRIADO

        if graph is not None:
            self._graph = graph # underlying simple graph


        # salvando ponteiros
        if adj_matrix is not None:
            self.adj_matrix = adj_matrix
        else:
            self.adj_matrix = self._graph.adj_matrix

import numpy as np
from sys import getsizeof

I = np.ones((20, 20))
print(getsizeof(I))
g = Graph(I)
mg = Graph(I)

print(getsizeof(g))
print(getsizeof(mg))
print(g.adj_matrix)
print(getsizeof(g.adj_matrix))
print(getsizeof(mg.adj_matrix))
print('---------------------')
print(id(I))
print(id(g.adj_matrix))
print(id(mg.adj_matrix))
