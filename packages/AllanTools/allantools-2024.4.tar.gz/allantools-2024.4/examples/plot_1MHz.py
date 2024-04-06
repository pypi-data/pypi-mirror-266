import allantools
import numpy as np

# frequency in Hz
# 1 MHz with 30 Hz noise
f = 1.0e6 + 30*np.random.randn(1000)
f_mean = np.average(f)
print("f mean = ", f_mean)
print("f stdev = ", np.std(f))
# compute fractional frequency time-series
y = f / f_mean
print("y mean = ", np.average(y))
print("y stdev = ", np.std(y))

# Compute a deviation using the Dataset class
a = allantools.Dataset(data=y, data_type='freq')
a.compute("oadev")

# Plot it using the Plot class
b = allantools.Plot()
b.plot(a, errorbars=True, grid=True)
# You can override defaults before "show" if needed
b.ax.set_xlabel("Tau (s)")
b.show()
