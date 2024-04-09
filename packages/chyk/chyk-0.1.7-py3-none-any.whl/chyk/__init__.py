import handcalcs.render
import forallpeople as u
u.environment('default')
from IPython.display import Latex
from numpy import sqrt, pi, cos, sin, tan, log10, log2, log, e, arctan, arccos, arcsin
import numpy as np
from math import atan2,acos,asin
sqrt = np.emath.sqrt
from matplotlib import pyplot as plt
from scipy.integrate import quad
from scipy.optimize import fsolve
from scipy.optimize import curve_fit
from scipy.constants import c
from latex2sympy2 import latex2sympy, latex2latex
import sympy as sym
from sympy import roots
from sympy.abc import x, a, b
from sympy import integrate
from sympy import lambdify
from sympy import Symbol
from sympy.solvers import solve
from sympy import re, im
from tabulate import tabulate
import pandas as pd
from fgmkr import fgmk, fgmk2, fgmk_help

# Separates imaginary and real components
def ri(imag):
    return [sp.re(imag), sp.im(imag)]

# Finds angle in degrees of an imaginary number
def ang(imag):
    return atan2(im(imag),re(imag))*180/pi

# Custom notation to pretty-fy outputs for phasor notation
deg = Symbol('^\circ')
deg_C = Symbol('^\circ\,C')
deg_K = Symbol('^\circ\,K')
aag = Symbol('\, Magnitude\, \, @ \,')
def cphas(mag_in, angle_in):
    return mag_in*aag + angle_in*deg

# Zero Shift Timescale
def zeroshift(raw):
    return raw - min(raw) if raw.size else np.array([])

# Embedded Separators
Part_A = Symbol('Part\, A\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :')
Part_B = Symbol('Part\, B\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :')
Part_C = Symbol('Part\, C\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :')
Part_D = Symbol('Part\, D\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :')

# Debugging Marker
mk = Symbol('marker \quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :')