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
    return [re(imag), im(imag)]

# Finds angle in degrees of an imaginary number
def ang(imag):
    return atan2(im(imag),re(imag))*180/pi

# Custom notation to pretty-fy outputs for phasor notation
deg = Symbol('^\circ')
deg_C = Symbol('^\circ\,C')
deg_K = Symbol('^\circ\,K')
def cphas(mag_in, angle_in):
    return f'{mag_in}' r'\,\, $\angle$' + f'\,{angle_in}' + r'$^\circ$'

# Phasor to Rectangular
def p2r(mag, phi):
    r_num = mag * (cos(phi) + sin(phi)*1j)
    if abs(r_num.real) < 1e-10: r_num = complex(0, r_num.imag)
    if abs(r_num.imag) < 1e-10: r_num = complex(r_num.real, 0)
    return r_num

# Phasor to Rectangular, Degree Inputs
def p2rd(mag, phi):
    return p2r(mag, phi*pi/180)

# Zero Shift Array Timescale
def zeroshift(raw):
    return raw - min(raw) if raw.size else np.array([])

# Embedded Separators
Part_A = Symbol('Part\, A\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :')
Part_B = Symbol('Part\, B\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :')
Part_C = Symbol('Part\, C\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :')
Part_D = Symbol('Part\, D\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :')

# Debugging Marker
mk = Symbol('marker \quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :\quad :')