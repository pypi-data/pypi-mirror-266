from sys import path
path.append('..')
import hiperwalk as hpw
import networkx as nx
import numpy as np
import scipy.sparse
import scipy.linalg

dim = 8
g = hpw.Hypercube(dim)
qw = hpw.Coined(g)
time = (int(np.pi/2 * np.sqrt(2**dim)), 1)
psi0 = qw.uniform_state()


def number_to_marked(num):
    """
    Binary representation of number indicates which
    vertices are going to be marked.

    For instance, if num = 5,
    bin(5) = 101 => vertices 2 and 0 are marked.
    """
    num = bin(num)
    i = -1
    marked = []
    while(num[i] != 'b'):
        if num[i] == '1':
            marked.append(-i - 1)
        i -= 1

    return marked

print("(marked, t_opt, prob)")
min_tuple = (-1, -1, 2)
max_tuple = (-1, -1, -1)

#for i in range(1, 2**(g.number_of_vertices())):
# for i in range(1, 10):
#     marked = number_to_marked(i)
#     qw.set_marked({'-I': marked})
#     states = qw.simulate(time, psi0)
#     probs = qw.success_probability(states)
#     t_opt = qw.optimal_runtime(psi0)
# 
#     if probs[t_opt + 1] > probs[t_opt]:
#         t_opt += 1
# 
#     # print((i, t_opt, probs[t_opt]))
# 
#     if (probs[t_opt] < min_tuple[2]):
#         min_tuple = (i, t_opt, probs[t_opt])
#     elif (probs[t_opt] > max_tuple[2]):
#         max_tuple = (i, t_opt, probs[t_opt])
# 
#     # hpw.plot_success_probability(time, probs)
#     # print()
# 
#     print("min_tuple: " + str(min_tuple))
#     print("max_tuple: " + str(max_tuple))
#     print()


# 0 and all numbers with 2 bits
marked = [0]
# for i in range(dim):
#     for j in range(i + 1, dim):
#         marked.append(2**i + 2**j)

print(marked)
print(len(marked))

from time import time as now

start = now()
qw.set_marked({'-I': marked})
states = qw.simulate(time, psi0)
probs = qw.success_probability(states)
t_opt = qw.optimal_runtime(psi0)
if probs[t_opt + 1] > probs[t_opt]:
    t_opt += 1
print(('?', t_opt, probs[t_opt]))

print(now() - start)
hpw.plot_success_probability(time, probs)
