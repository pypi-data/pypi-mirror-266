import allantools as at

x1 = at.noise.white(num_points=1024)
x2 = at.noise.pink(num_points=1024)
# produces wrong results:
ds1 = at.Dataset(x1)
ds2 = at.Dataset(x2)
r1 = ds1.compute('oadev')
r2 = ds2.compute('oadev')
print("r1",r1['stat'][0])
print("r1",r2['stat'][0])

# produces correct results:
ds1 = at.Dataset(x1)
r1 = ds1.compute('oadev')
ds2 = at.Dataset(x2)
r2 = ds2.compute('oadev')
print("r1",r1['stat'][0])
print("r2",r2['stat'][0])
