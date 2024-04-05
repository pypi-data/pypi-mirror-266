from sys import path
path.append('..')
import hiperwalk as hpw
import networkx as nx
import numpy as np
import scipy.sparse
import scipy.linalg

dim = 9
# hypercube = nx.hypercube_graph(dim)
# adj = nx.adjacency_matrix(hypercube, dtype=np.int8)
# del hypercube
# adj = adj + scipy.sparse.identity(adj.shape[0], dtype=np.int8)
# g = hpw.Graph(adj)

g = hpw.Hypercube(dim)

qw = hpw.Coined(g, marked={'-I': [0, 1]})
time = (int(np.pi/2 * np.sqrt(2**dim)), 1)
states = qw.simulate(time=time, state=qw.uniform_state())
probs = qw.success_probability(states)

# hpw.plot_success_probability(time, probs)

# a, b = np.linalg.eig(qw.get_evolution().todense())
c, d = scipy.sparse.linalg.eigs(qw.get_evolution())
# print(b)
# print()
# print(a)
# print(len(a))
# print()
print(c)
print(len(c))
# uniform = qw.uniform_state()
# b = b.T
# inner_product = [uniform @ b[i] for i in range(len(b))]
# prob = np.abs(inner_product)
# print(prob)
# print(np.sum(prob))
# print(a[:10])
