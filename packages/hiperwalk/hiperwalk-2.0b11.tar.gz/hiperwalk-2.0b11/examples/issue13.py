from sys import path
path.append('..')
import hiperwalk as hpw
import matplotlib.pyplot as plt
import numpy as np
import scipy

dim = 10
g = hpw.Grid((dim, dim))
N = g.number_of_vertices()
qw = hpw.Coined(graph=g, coin='G', shift='ff', marked={'-I': [(dim//2, dim//2)]})
psi0 = qw.uniform_state()
num_steps = int(1.5*np.sqrt(N*np.log(N)))
states = qw.simulate(time=(num_steps, 1),
                     initial_state=psi0,
                     hpc=False)
succ_prob = qw.probability_distribution(states)
hpw.plot_probability_distribution(succ_prob, graph=g, animate=True, rescale=True)
