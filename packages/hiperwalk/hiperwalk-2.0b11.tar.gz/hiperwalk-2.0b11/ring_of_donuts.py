import numpy as np
import networkx as nx
import hiperwalk as hpw
import matplotlib.pyplot as plt

for grid_dim in range(4, 8):
    ring_dim = 10
    print("BEGIN " + str((grid_dim, ring_dim)))

    list_of_donuts = [nx.grid_graph((grid_dim, grid_dim), periodic=True)
                      for i in range(ring_dim)]

    ring_of_donuts = nx.union(list_of_donuts[0], list_of_donuts[1],
                              rename=("D0-", "D1-"))

    # disjoint union
    for i in range(2, ring_dim):
        ring_of_donuts = nx.union(ring_of_donuts, list_of_donuts[i],
                                  rename=("", "D" + str(i) + "-"))

    # vertices identification

    for x in range(2):
        for y in range(2):
            u = (x, y) # u \in {(0, 0), (0, 1), (1, 0), (1, 1)}
            for donut_id in range(ring_dim):
                v = (u[0] + grid_dim // 2, u[1] + grid_dim // 2)
                u_id = "D" + str(donut_id) + "-" + str(u)
                v_id = "D" + str((donut_id + 1) % ring_dim) + "-" + str(v)
                nx.identified_nodes(ring_of_donuts, u_id, v_id, copy=False)

    # print(ring_of_donuts.nodes())
    # print(nx.adjacency_matrix(ring_of_donuts))

    marked_vertex = 0
    qw = hpw.Coined(nx.adjacency_matrix(ring_of_donuts),
            coin='G', marked={'-I': marked_vertex})

    num_vert = ring_of_donuts.number_of_nodes()
    states = qw.simulate(time=(2*int(np.sqrt(num_vert*np.log(num_vert))),
                               1),
                         initial_state=qw.uniform_state(),
                         hpc=False)

    probs = qw.probability_distribution(states)
    # probs = np.array(qw.probability_distribution(states))
    # probs = np.reshape(probs,
    #                    (len(states), qw._graph.number_of_vertices()))
    # print(type(probs))
    p_succ = probs[:,marked_vertex]

    t_opt = np.argmax(p_succ)

    plt.plot(np.arange(len(p_succ)), p_succ,
             label=(r"$\sqrt{N}=$" + str(grid_dim)
                    + ", g=" + str(ring_dim)),
             alpha=0.5)
    plt.ylabel("p_succ", fontsize=14)
    plt.xlabel("t", fontsize=14)

plt.legend()
plt.show()
