
# import allantools as at
from matplotlib import pyplot as plt
import numpy as np


def b1_2(N):
    return float(N)*(float(N)+1.0)/6.0


def b1(N, mu):
    up = N*(1.0-pow(N, mu))
    down = 2*(N-1.0)*(1-pow(2.0, mu))
    return up/down


Ns = np.logspace(2, 6, 20)
Ns = [int(x) for x in Ns]
mu = 2
b1_mu = [b1(x, mu) for x in Ns]
b1_2 = [b1_2(x) for x in Ns]
plt.figure()
plt.loglog(Ns, b1_mu, 'o')
plt.loglog(Ns, b1_2, '--')
for (a, b) in zip(b1_mu, b1_2):
    print(a/b)
plt.show()
