import allantools as allan
from matplotlib import pyplot as plt
import gzip


def read_datafile(filename):
    p = []
    if filename[-2:] == 'gz':
        with gzip.open(filename, mode='rt') as f:
            for line in f:
                if not line.startswith("#"):  # skip comments
                    p.append(float(line))
    else:
        with open(filename) as f:
            for line in f:
                if not line.startswith("#"):  # skip comments
                    p.append(float(line))
    return p


def read_resultfile(filename):
    rows = []
    row = []
    with open(filename) as f:
        for line in f:
            if not line.startswith("#"):  # skip comments
                row = []
                l2 = line.split(" ")
                l2 = [_f for _f in l2 if _f]
                for n in range(len(l2)):
                    row.append(float(l2[n]))
                rows.append(row)
    return rows


def read_stable32(resultfile, datarate):
    devresults = read_resultfile(resultfile)
    print("Read ", len(devresults), " rows from ", resultfile)
    rows = []
    # parse textfile produced by Stable32
    for row in devresults:
        if len(row) == 7:  # typical ADEV result file has 7 columns of data
            d = {}
            d['m'] = row[0]
            d['tau'] = row[0] * (1 / float(datarate))
            d['n'] = row[2]
            d['alpha'] = row[3]
            d['dev_min'] = row[4]
            d['dev'] = row[5]
            d['dev_max'] = row[6]

            rows.append(d)
        elif len(row) == 4:  # the MTIE/TIErms results are formatted slightly differently
            d = {}
            d['m'] = row[0]
            d['tau'] = row[0] * (1 / float(datarate))
            d['n'] = row[2]
            d['dev'] = row[3]
            rows.append(d)
    return rows


rows = read_stable32('phase_dat_mtie.txt', 1.0)
x = read_datafile('PHASE.DAT')
(ftaus, fdevs, ferrs, fns) = allan.mtie_phase_fast(x)
(taus, devs, errs, ns) = allan.mtie(x)

print(ftaus, fdevs, fns)
print(rows)
plt.figure()
plt.loglog([r['tau'] for r in rows], [r['dev'] for r in rows], 'bo')
plt.loglog([t for t in ftaus], fdevs, 'r*')
plt.loglog(taus, devs, 'gd')

plt.grid()
plt.show()
