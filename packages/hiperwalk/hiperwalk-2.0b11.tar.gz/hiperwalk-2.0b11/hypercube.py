import numpy as np
import hiperwalk as hpw

dim = 5
g = hpw.Hypercube(dim)

# marcar 0 e seus vizinhos
marked = [0] + list(g.neighbors(0))
marked = set(marked)

qw = hpw.Coined(g, shift='ff', coin='G',
                marked={'-I': marked},
                hpc=False)

# time = (int(2**(dim/2)), 1)
# states = qw.simulate(time=time,
#                      state=qw.uniform_state(),
#                      hpc=False)
# probs = qw.success_probability(states)
# hpw.plot_success_probability(time, probs)

def M2_func(marked_vertex):
    neigh = set(g.neighbors(marked_vertex))
    intersection = neigh.intersection(marked)
    ret = [((marked_vertex, neigh)) for neigh in intersection]
    return ret

def M1_func(marked_vertex):
    neigh = set(g.neighbors(marked_vertex))
    intersection = neigh.intersection(marked)
    ret = [((marked_vertex, neigh)) for neigh in intersection]
    return ret

M2 = []
for m in marked:
    M2 += M2_func(m)
M2 = qw.state([(1, arc) for arc in M2])

def M1_func(marked_vertex):
    neigh = set(g.neighbors(marked_vertex))
    difference = neigh.difference(marked)
    ret = [((marked_vertex, neigh)) for neigh in difference]
    return ret
M1 = []
for m in marked:
    M1 += M1_func(m)
M1 = qw.state([(1, arc) for arc in M1])

def barM1_func(unmarked_vertex):
    neigh = set(g.neighbors(unmarked_vertex))
    difference = neigh.difference(unmarked)
    ret = [((unmarked_vertex, neigh)) for neigh in difference]
    return ret
barM1 = []
unmarked = {i for i in range(g.number_of_vertices())}.difference(marked)
for u in unmarked:
    barM1 += barM1_func(u)
barM1 = qw.state([(1, arc) for arc in barM1])

def barM2_func(unmarked_vertex):
    neigh = set(g.neighbors(unmarked_vertex))
    difference = neigh.difference(marked)
    ret = [((unmarked_vertex, neigh)) for neigh in difference]
    return ret
barM2 = []
for u in unmarked:
    barM2 += barM2_func(u)
barM2 = qw.state([(1, arc) for arc in barM2])

### FORM ORTHONORMAL BASIS OF THE SUBSPACE
subspace = [M2, M1, barM1, barM2]
# identity = np.zeros((len(subspace), len(subspace)))
# for i in range(len(subspace)):
#     for j in range(len(subspace)):
#         identity[i,j] = subspace[i] @ subspace[j]
# 
# print(identity)
# ###########################################
# 
# sim_res = qw.simulate(time=1, state=barM1, hpc=False)
# sim_res = sim_res[0]
# for state in subspace:
#     inner_prod = state @ sim_res
#     sim_res -= inner_prod * state
# 
# new1 = sim_res/np.linalg.norm(sim_res)
# subspace.append(new1)
# 
# ###########################################
# 
# sim_res = qw.simulate(time=2, state=barM2, hpc=False)
# sim_res = sim_res[0]
# for state in subspace:
#     inner_prod = state @ sim_res
#     sim_res -= inner_prod * state
# 
# new2 = sim_res/np.linalg.norm(sim_res)
# subspace.append(new2)

############################################################
for init_state in subspace:
    sim_res = qw.simulate(time=1, state=init_state, hpc=False)
    sim_res = sim_res[0]
    sum_prob = 0
    for state in subspace:
        inner_prod = state @ sim_res
        print(inner_prod)
        sum_prob += inner_prod**2

    print('prob: ' + str(sum_prob))
    print()
