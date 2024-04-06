import matplotlib.pyplot as plt
import allantools as at
import time

# benchmark for mtotdev and htotdev
# AW2019-07-09


pts = []
times = []
for n_exponent in range(6, 12):
    n_pts = pow(2, n_exponent)
    x = at.noise.white(n_pts)
    t0 = time.time()
    (taus, devs, ers, ns) = at.htotdev(x)
    t1 = time.time()
    dt = (t1-t0)/float(n_pts)
    times.append(dt)
    pts.append(n_pts)
    print(n_pts, (t1-t0), dt)

plt.figure()
plt.loglog(pts, times, 'o')
plt.grid()
plt.show()
