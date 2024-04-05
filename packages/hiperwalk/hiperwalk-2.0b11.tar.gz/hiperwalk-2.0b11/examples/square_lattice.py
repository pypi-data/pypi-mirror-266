from sys import path
path.append('..')
import hiperwalk as hpw

g = hpw.SquareLattice((3, 3), periodic=False)
print(g._adj_matrix.shape)
print(g._adj_matrix.data)
print(g._adj_matrix.indices)
print(g._adj_matrix.indptr)
print(g.adjacency_matrix().todense())
