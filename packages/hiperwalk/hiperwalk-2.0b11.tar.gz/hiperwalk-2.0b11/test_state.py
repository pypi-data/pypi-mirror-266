import numpy as np
import hiperwalk as hpw

dim = 10
g = hpw.Grid((dim, dim))
qw = hpw.Coined(g)
psi = qw.state((1, (0, 1)), [1, 1], (1, 2))
psi1 = qw.state((1, ([0, 0], [1, 0])),
                [[1, (0, dim - 1)],
                 (1, [(0, 0), [0, 1]])])
psi2 = qw.state([(1, [0, 0], [1, 0]),
                 [1, 0, dim - 1]],
                (1, (0, 0), [0, 1]))

print(np.all(psi == psi1))
print(np.all(psi1 == psi2))
print(psi.dtype)
psi = qw.state((1j, 0), [[1, 1], (1, 2)])
print(psi.dtype)

print('===========')

qw = hpw.ContinuousTime(g, 1)
psi = qw.state((1, 0), [1, 1], (1, 2))
psi1 = qw.state((1, [0, 0]), [[1, (1, 0)], (1, 2)])
psi2 = qw.state(((1, 0), [1, 1]), (1, (2, 0)))
psi3 = qw.state([(1, 0), [1, 1], (1, 2)])

print(np.all(psi == psi1))
print(np.all(psi1 == psi2))
print(np.all(psi2 == psi3))
print(psi.dtype)
psi = qw.state((1j, 0), [[1, 1], (1, 2)])
print(psi.dtype)
