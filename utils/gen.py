import numpy as np
import pandas as pd
import os, sys
from librosa import frames_to_time
from time import time, sleep
from datetime import timedelta


def show_status(perc, lapsed_time=None, tstart=None,size=20):
    sys.stdout.write('\r')
    if lapsed_time is None and tstart is not None:
        lapsed_time = time() - tstart
    if lapsed_time is not None and perc!=0:
        time_left = str(timedelta(seconds=int(lapsed_time / perc - lapsed_time)))
    else:
        time_left = 'n/a'
    if int(perc*100)==100:
        if lapsed_time is not None: total_time = str(timedelta(seconds=int(lapsed_time)))
        else: total_time = 'n/a'
        sys.stdout.write("[{perc_bar:<{size}}] {perc:.2%} \nTotal Time: {total_time:<15}".format(perc_bar='='*int(perc*size),
                                                                                                 perc=(perc),
                                                                                                 total_time=total_time,
                                                                                                 size=size))
        sys.stdout.write('\n')
    else:
        sys.stdout.write("[{perc_bar:<{size}}] {perc:.2%} {time_left:<15}".format(perc_bar='='*int(perc*size),
                                                                                  perc=(perc),
                                                                                  time_left=time_left,
                                                                                  size=size))
    sys.stdout.flush()
    sleep(0.05)


def createx(data, fs, istime=True):
    '''Creates an time or Frquency x range signal.

    :param data: (ndarray,list,int,float) data or length of data
    :param fs: (int,float) sample rate
    :param istime: Whether xrange represents time or frequency (hz) axis
    :return: array
    '''
    if hasattr(data,"__len__"): N = len(data)
    else: N = int(data)
    if istime is True: return np.linspace(0, N/float(fs), N)
    else: return np.linspace(-fs/2, fs/2, N)


def clamp(value, minval=-np.inf, maxval=np.inf,dtype=None):
    '''

    Clamps Values to ensure all values stay within a certain bounds

    :param value:
    :param minval:
    :param maxval:
    :param dtype:
    :return:
    '''
    if dtype is None: dtype = type(value)
    return dtype(min(max(value, minval), maxval))


def norm(data,minval=None,maxval=None, Nmin = 0, Nmax = 1, axis=0, norm_type='full'):
    '''
    Normalize data

    :param data: {list, np.ndarray} [shape=(d, n)]
        signal that is normalized
    :param minval: {float, None}
        Min value of signal. if 'None', minval = min of data
    :param maxval: {float > minval, None}
        Max value of signal. if 'None', maxval = max of data
    :param Nmin: {float}
        Resulting normalized min value (if norm_type = 'full')
    :param Nmax: {float > Nmin}
        Resulting Normalized Max value
    :param axis: data.ndim > int >=0
        axis by which normalization occurs
    :param norm_type: {'max','full'}
        'max'   - divide by maxval
        'full'  - map bounds of data to [Nmin, Nmax]
    :return: np.ndarray
    '''
    data = np.array(data)
    if not (isinstance(maxval,(int,long,float))):
        maxval = None
    if not (isinstance(minval,(int,long,float))):
        minval = None
    if not (maxval is None or minval is None) and maxval <= minval:
        maxval = None
        minval = None
    if norm_type == 'full':
        if not minval or np.isnan(minval):
            minval = np.min(data,axis=axis,keepdims=True if axis is not None else False)
        if not maxval or np.isnan(maxval):
            maxval = np.max(data,axis=axis,keepdims=True if axis is not None else False)
        return (data - minval)/(maxval-minval) * (Nmax - Nmin) + Nmin
    else: #norm_type == 'max'
        if not maxval or np.isnan(maxval):
            maxval = np.max(np.abs(data),axis=axis,keepdims=True if axis is not None else False)
        return data / maxval

