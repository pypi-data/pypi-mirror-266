import hiperwalk as hpw
import matplotlib.pyplot as plt
import numpy as np

qw = hpw.Coined(graph=hpw.Grid(41),
                shift='ff',
                coin='G',
                marked={'-I': [0]},
                hpc=False)

# t_opt = qw.optimal_runtime(delta_time=1, hpc=False)
# 
# psi0 = qw.uniform_state()
# states = qw.simulate(time=(2*t_opt, 1),
#                      initial_state=psi0,
#                      hpc=False)
# p_succ = qw.success_probability(states)
# del states
# 
# plt.plot(np.arange(len(p_succ)), p_succ)
# plt.scatter(t_opt, p_succ[t_opt], color='r', marker='o')
# plt.show()

print(qw.max_success_probability(delta_time=2, hpc=False))
