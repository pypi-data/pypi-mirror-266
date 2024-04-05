import hiperwalk as hpw

dim = 41
lat = hpw.Grid((dim, dim))
qw = hpw.Coined(graph=lat, hpc=False, coin='H', shift='p')

c = dim//2
psi0 = qw.state( [1, ((c, c), (c + 1, c))],
                 [-1, ((c, c), (c - 1, c))])
states = qw.simulate(time=(dim, 1), initial_state=psi0)
probs = qw.probability_distribution(states)

hpw.plot_probability_distribution(probs, graph=lat, rescale=True)
