from sys import path
path.append('..')
import hiperwalk as hpw

g = hpw.Hypercube(3)
print(g.adjacency_matrix().todense())
print(g._adj_matrix.data)
print(g.dimension())
print(g.degree(0))
