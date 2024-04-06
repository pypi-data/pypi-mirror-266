#!/usr/bin/python

"""
    This test is for the memory-consumtion of mtie()
    
    The older rolling-window algorithm can be used for small
    datasets, but memroy allocation of 5 Gb was reported for an array
    of size ~400k datapoints in issue #82
    
    Here we try to test for large datasets - which gives test-coverage
    for the new algorithm also.
"""

import sys
sys.path.append("..")

import allantools as allan
from allantools import noise
import numpy

def _test( function, data):

    (taus2,devs2,errs2,ns2) = function(data, rate=1.0)

    print("test_mtie_memory len(data)=",len(data), " OK.")
    
def NOtest_mtie_memory():
    for N in numpy.logspace(3,7,20):
        phase_white = noise.white(int(N))
        _test( allan.mtie, phase_white)

if __name__ == "__main__":
    NOtest_mtie_memory()
