from sys import path
path.append('..')
import hiperwalk as hpw
import networkx as nx
import numpy as np
import scipy.sparse

dim = 100
g = hpw.Grid((dim, dim), diagonal=True, periodic=True)
qw = hpw.Coined(g, shift='ff', coin='G', marked={'-G': [(0,0), (50, 50)]})
time = (int(dim*np.sqrt(np.log2(dim**2))), 1)
states = qw.simulate(time=time, state=qw.uniform_state())
probs = qw.success_probability(states)

hpw.plot_success_probability(time, probs)
