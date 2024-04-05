import hiperwalk as hpw

dims = range(5, 11)

qw_gen = (hpw.Coined(
              hpw.Hypercube(d),
              marked={'-G': [0]})
          for d in dims)

hpw.plot_max_success_probability(qw_gen, 'Dimension', dims)
