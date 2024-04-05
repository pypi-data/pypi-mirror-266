import hiperwalk as hpw

g = hpw.Grid(40)
qw = hpw.Coined(graph=g, shift='ff', marked={'-G': [(20, 20)]})
psif = qw.simulate(time=(100, 10), initial_state=qw.uniform_state(), hpc=False)
probs = qw.probability_distribution(psif)
hpw.plot_probability_distribution(probs, graph=g, rescale=True)
