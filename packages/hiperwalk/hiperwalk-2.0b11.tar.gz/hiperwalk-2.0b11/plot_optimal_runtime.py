import hiperwalk as hpw

dims = range(5, 11)

qw_gen = (hpw.Coined(
              hpw.Hypercube(d),
              marked={'-G': [0]})
          for d in dims)

hpw.plot_optimal_runtime(qw_gen, 'Dimension', dims)
