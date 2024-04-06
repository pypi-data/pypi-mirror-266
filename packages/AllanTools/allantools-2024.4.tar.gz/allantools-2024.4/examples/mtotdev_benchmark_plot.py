import matplotlib.pyplot as plt
# import allantools as at
# import time
import numpy
# benchmark for mtotdev and htotdev
# AW2019-07-09


mtot_old = [(64, 0.102194786072, 0.00159679353237),
            (128, 0.405575990677, 0.00316856242716),
            (256, 1.5975189209, 0.00624030828476),
            (512, 6.43926692009, 0.0125766932033),
            (1024, 25.6946251392, 0.0250924073625),
            (2048, 103.717272997, 0.0506431997055)]


mtot_new = [(64, 0.0179510116577, 0.000280484557152),
            (128, 0.0634391307831, 0.000495618209243),
            (256, 0.221443891525, 0.000865015201271),
            (512, 0.797779798508, 0.00155816366896),
            (1024, 3.00882697105, 0.00293830758892),
            (2048, 11.6157557964, 0.00567175575998)]


plt.figure()
plt.loglog([x[0] for x in mtot_old], [x[1]
                                      for x in mtot_old], 'o', label='old')
n = numpy.logspace(1, 4, 100)
c_old = 104/pow(2048.0, 2)
plt.loglog(n, [c_old*pow(x, 2) for x in n], 'b--',
           label='%.3f us * N^2' % (c_old*1e6))

plt.loglog([x[0] for x in mtot_new],
           [x[1] for x in mtot_new], 'o', label='improved')
c_new = 11.6/pow(2048.0, 2)
plt.loglog(n, [c_new*pow(x, 2) for x in n], 'g--',
           label='%.3f us * N^2' % (c_new*1e6))

plt.legend()
# plt.loglog
plt.xlabel('Input size / # points')
plt.ylabel('CPU time / seconds')
plt.title('AllanTools 2019.07 improved speed for mtotdev(), AW2019-07-09')
plt.grid()
plt.show()
