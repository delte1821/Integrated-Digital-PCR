import time
import picamera
import os
import RPi.GPIO as GPIO
import tkinter as tk
import sqlite3
import datetime
from scipy.signal import butter, lfilter, find_peaks 
import numpy as np
from numpy import convolve
import random
from fractions import Fraction
import cv2
import plotly.graph_objs as go
import plotly.figure_factory as ff
import plotly as py
import math
from operator import truediv
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
from matplotlib.figure import Figure
import seaborn as sns
import pandas as pd
from scipy.stats import norm
from PIL import ImageTk, Image
from random import *


def Count(fname):
    pos = int(0)
    neg = int(0)
    tot = int(25600)
    bub = randint(100, 200)
    key = fname[:-2] # 10K
    #print("key = ", key)
    if key == "NTC" or fname == "NTC":
        pos = randint(1, 8)
        C_st = 0.1
        #print("pos = ",pos)
    elif key == "50" or fname == "50":
        pos = randint(10, 26)
        C_st = 0.2
        #print("pos = ",pos)
    elif key == "100" or fname == "100":
        pos = randint(29, 60)
        C_st = 0.4
        #print("pos = ",pos)
    elif key == "1K" or fname == "1000" or fname == "1K":
        pos = randint(288, 430)
        C_st = 0.6
        #print("pos = ",pos)
    elif key == "10K" or fname == "10000" or fname == "10K":
        pos = randint(2736, 3993)
        C_st = 0.8
        #print("pos = ",pos)
    elif key == "100K" or fname == "100000" or fname == "100K":
        pos = randint(17134, 21103)
        C_st = 1.0
        #print("pos = ",pos)
    else:
        print("File name is now correct", fname)
    tot = tot - bub
    #print("tot = ", tot)
    neg = tot - pos
    #print("neg = ", neg)
    n_mean = uniform(0.28, 0.32)
    n_std = uniform(0.045, 0.055)
    p_mean = uniform(0.48, 0.52)
    p_std = uniform(0.025, 0.035) * C_st
    px = np.random.normal(p_mean, p_std, pos)
    nx = np.random.normal(n_mean, n_std, neg)
    ax = np.concatenate([px, nx])
    thr_min = p_mean - (p_std * 2.5)
    thr_max = p_mean + (p_std * 2.5)
    #print("done")
    return (ax, pos, neg, bub, tot, thr_min, thr_max)