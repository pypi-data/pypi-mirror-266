#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  4 20:48:19 2023

@author: anders
"""

# numpy.convolve

import numpy
import matplotlib.pyplot as plt


def Wpi(t, tau):
    # Pi counter
    if t > 0 and t <= tau:
        return 1.0/(tau)
    else:
        return 0.0

def Wlambda(t, tau):
    # Lambda counter
    if t > 0 and t <= tau:
        return 1.0/(tau)*t
    elif t > tau and t <= 2*tau:
        return 1.0/(tau)-(1.0/tau)*(t-tau)
    else:
        return 0.0

def Womega(t, tau):
    # omega counter
    if t > 0 and t <= tau:
        return 3.0/(2*tau) - 6*pow(t-tau/2,2)/pow(tau,3)
    else:
        return 0.0
    
def step(t):
    if t>0:
        return 1.0
    else:
        return -1.0
    
t = numpy.linspace(-5,5,50000)


w_pi = numpy.array([Wpi(x,1.0) for x in t])
w_lam = numpy.array([Wlambda(x,1.0) for x in t])
w_om = numpy.array([Womega(x,1.0) for x in t])
w_step = numpy.array([step(x) for x in t])

cpi = numpy.convolve(w_pi,w_step,mode='same')/len(t)
clam = numpy.convolve(w_lam,w_step,mode='same')/len(t)
com = numpy.convolve(w_om,w_step,mode='same')/len(t)
plt.figure()
plt.subplot(1,3,1)
plt.plot(t,w_pi)
plt.plot(t,w_step)
plt.plot(t,cpi)
plt.grid()
plt.xlim((-0.1,1.1))

plt.subplot(1,3,2)
plt.plot(t,w_lam)
plt.plot(t,w_step)
plt.plot(t,clam)
plt.grid()
plt.xlim((-0.1,2.1))

plt.subplot(1,3,3)
plt.plot(t,w_om)
plt.plot(t,w_step)
plt.plot(t,com)
plt.grid()
plt.xlim((-0.1,1.1))
