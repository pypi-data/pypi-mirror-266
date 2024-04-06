import test_nbs14_1000point

fdata = test_nbs14_1000point.nbs14_1000()
print(fdata)

with open('nbs14.txt','w') as f:
    for (i,x) in enumerate(fdata):
        print(i,x)
        f.write('%04d %.12f\n'%(i,x))
