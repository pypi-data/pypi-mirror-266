import hiperwalk as hpw

g = hpw.Cycle(20)
qw = hpw.Coined(g)
psi0 = qw.state([1, 0], [1, 2])
states = qw.simulate((10, 1), psi0)

print("=============================")
print(qw.probability_distribution(psi0))
print()
print(qw.probability_distribution(states))
print("=============================")
print(qw.probability(psi0, [0, 2, 4]))
print()
print(qw.probability(states, [0, 2, 4]))
