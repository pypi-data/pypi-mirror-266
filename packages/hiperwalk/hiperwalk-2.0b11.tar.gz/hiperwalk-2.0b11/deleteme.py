import numpy as np
import scipy.sparse
import hiperwalk as hpw

num_vert = 5
data = np.ones(num_vert**2)
indices = [(u + shift) % num_vert
           for u in range(num_vert)
           for shift in range(num_vert)]
indptr = np.arange(0, num_vert**2 + 1, num_vert)
adj_matrix = scipy.sparse.csr_array((data, indices, indptr))
# creating graph with non-default order of neighbors
g = hpw.Graph(adj_matrix)
# testing the order of neighbors
for u in range(num_vert):
    print(g.neighbors(u))

print('----------------------')

data = [u + v + 1 for u in range(num_vert)
        for v in indices[indptr[u]:indptr[u+1]]]

adj_matrix = scipy.sparse.csr_array((data, indices, indptr))

# creating multigraph
g = hpw.Multigraph(adj_matrix)

for u in range(num_vert):
    print(g.neighbors(u))

# checking if multigraph was created properly
print(
    np.all(np.array(
            [g.number_of_edges(u, v) == u + v + 1
            for u in range(num_vert)
            for v in range(num_vert)]) == True)
)
