# -*- coding: utf-8 -*-
#   Copyright (C) 2023-2024 Samuele Carcagno <sam.carcagno@gmail.com>
#   This file is part of audiometry_trainer

#    audiometry_trainer is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    audiometry_trainer is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with audiometry_trainer.  If not, see <http://www.gnu.org/licenses/>.

from .pyqtver import*
if pyqtversion == 5:
    from PyQt5 import QtGui, QtCore
elif pyqtversion == 6:
    from PyQt6 import QtGui, QtCore
    
from numpy import sin, cos, pi, sqrt, abs, arange, floor, zeros, mean, concatenate, convolve, correlate, angle, real, log2, log10, int_, linspace, repeat, ceil, unique, hamming, hanning, blackman, bartlett, round, transpose, flipud, amax
from numpy.fft import rfft, irfft, fft, ifft
from scipy.signal import firwin2
import copy

def ifelse(cnd, vl1, vl2):
    if cnd == True:
        out = vl1
    else:
        out = vl2
    return out

def pltColorFromQColor(qcolor):
    col = (qcolor.red()/255., qcolor.green()/255., qcolor.blue()/255.)
    return col

def scaleRGBTo01(col):
    col = tuple(el/255 for el in col)
    return col            

def log_10_product(x, pos):
    """The two args are the value and tick position.
    Label ticks with the product of the exponentiation"""
    return '%1i' % (x)

