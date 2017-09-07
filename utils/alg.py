import numpy as np
import pandas as pd
import scipy as sp


def moving_window(data, fs=22050, tm_window=0.1, N=None, applied_func=np.sum, applied_axis=0, hop_length=1, **kwargs):
    if N is None: N = max(2,int(fs*tm_window))
    # TODO: error thrown when N = 2
    def _wind(data, N, moving_window_func=np.sum,hop_length=1, **kwargs):
        res = np.zeros(len(data))
        res[:N//2] = moving_window_func(data[:N],**kwargs)
        res[-N//2:] = moving_window_func(data[-N:],**kwargs)
        shape = data.shape[:-1] + (data.shape[-1] - N + 1, N)
        strides = data.strides + (data.strides[-1],)
        res[N//2:-N//2+1] = moving_window_func(np.lib.stride_tricks.as_strided(data, shape=shape, strides=strides),axis=-1)
        return res[::hop_length]
    if data.ndim == 2:
        return np.apply_along_axis(_wind, applied_axis, data, N, applied_func, hop_length, **kwargs)
    else:
        return _wind(data, N=N, moving_window_func=applied_func, hop_length=hop_length, **kwargs)


def pandas_wind(data, N=None, fs=22050, tm_window=0.1, apply_func=np.sum,center=True,win_type=None,fill_nans=True,
                return_nans=False,applied_axis=0, **win_kwargs):
    '''
    Moving Statistical Aggregate Window Function

    :param data: np.ndarray or pd.DataFrame or pd.Series [shape=(d, 1 or 2)]
    :param N: int > 0
        Window size, in samples, of rolling window
    :param fs: int or float > 0 or None
        Sample frequency of time-based signals (used to calculate parameter N if N is None)
    :param tm_window: int or float > 0
        Time-length of rolling window (only used if N is None)
    :param apply_func: str or aggregate function (map numeric array -> numeric value)
        str option enables use of built-in, highly efficient pandas rolling statistical functions
        str options include:
        -   'mean': mean
        -   'median': median
        -   'sum': summation
        -   'rms': root mean squared
        -   'max': maximum
        -   'min': minimum
        -   'std': standard deviation
        -   'var': variance
        -   'skew': skewness
        -   'kurt': kurtosis
        -   'quantile': quantiles (default keyword argument is quantile= decimal between (0,1) )
    :param win_type: str
        window type options to apply window value weights to rolling window functions.
        Aggregate function defaults to mean. options include:
        -   'boxcar'
        -   'triang'
        -   'blackman'
        -   'hamming'
        -   'bartlett'
        -   'parzen'
        -   'bohman'
        -   'blackmanharris'
        -   'nuttall'
        -   'barthann'
        -   'kaiser'
                beta=1
        -   'gaussian'
                std=1
        -   'general_gaussian'
                power=1
                width=1
        -   'slepian'
                width=1
    :param applied_axis: data.ndim > int >=0
    :param center: bool
    :param return_nans: bool
    :param fill_nans: bool
    :param win_kwargs:
    :return:
    '''
    orig_pd_obj = True
    if data.ndim == 2:
        if not isinstance(data,pd.core.frame.DataFrame):
            data = pd.DataFrame(data)
            orig_pd_obj = False
    elif data.ndim ==1:
        if not isinstance(data,pd.core.series.Series):
            data = pd.Series(data)
            orig_pd_obj = False
        applied_axis = 0
    else: return data
    if N is None:
        N = int(fs*tm_window)
        if N > len(data): return data
    N = int(N)
    # TODO: win_type='blackman' prompts extremely slow function speed. Figure out why...
    def _aggregate(data,N,apply_func,win_type,center=center,applied_axis=0,special_kwargs={},**func_kwargs):
        try:
            if isinstance(apply_func,str):
                if apply_func == 'rms':
                    windowed_data = (data**2).rolling(window=N,center=center,axis=applied_axis,win_type=win_type)
                else:
                    windowed_data = data.rolling(window=N,center=center,axis=applied_axis,win_type=win_type)
                if apply_func == 'mean':
                    aggregated_data = windowed_data.mean(**special_kwargs)
                elif apply_func == 'median':
                    aggregated_data = windowed_data.median(**special_kwargs)
                elif apply_func == 'sum':
                    aggregated_data = windowed_data.sum(**special_kwargs)
                elif apply_func == 'rms':
                    aggregated_data = np.sqrt(windowed_data.mean(**special_kwargs).sqrt())
                elif apply_func == 'max':
                    aggregated_data = windowed_data.max(**special_kwargs)
                elif apply_func == 'min':
                    aggregated_data = windowed_data.min(**special_kwargs)
                elif apply_func == 'std':
                    aggregated_data = windowed_data.std(**special_kwargs)
                elif apply_func == 'var':
                    aggregated_data = windowed_data.var(**special_kwargs)
                elif apply_func == 'skew':
                    aggregated_data = windowed_data.skew(**special_kwargs)
                elif apply_func == 'kurt':
                    aggregated_data = windowed_data.kurt(**special_kwargs)
                elif apply_func == 'quantile':
                    aggregated_data = windowed_data.quantile(func_kwargs.get('quantile',0.5),**special_kwargs)
                else: aggregated_data = windowed_data.mean(**special_kwargs)
            else:
                windowed_data = data.rolling(window=N,center=center,axis=applied_axis,win_type=win_type)
                aggregated_data = windowed_data.apply(apply_func,**special_kwargs)
        except:
            windowed_data = data.rolling(window=N,center=center,axis=applied_axis,win_type=win_type)
            aggregated_data = windowed_data.mean(**special_kwargs)
        return aggregated_data
    win_types = ['boxcar','triang','blackman','hamming','bartlett','parzen','bohman','blackmanharris',
                 'nuttall','barthann','kaiser','gaussian','general_gaussian','slepian']

    if win_type is not None and win_type not in win_types: win_type = None
    if win_type == 'kaiser':
        special_kwargs = {'beta':win_kwargs.get('beta',1)}
    elif win_type == 'gaussian':
        special_kwargs = {'std':win_kwargs.get('std',1)}
    elif win_type == 'general_gaussian':
        special_kwargs = {'power':win_kwargs.get('power',1),
                          'width':win_kwargs.get('width',1)}
    elif win_type == 'slepian':
        special_kwargs = {'width':win_kwargs.get('width',1)}
    else:
        special_kwargs = {}
    res = _aggregate(data,N,apply_func=apply_func,win_type=win_type,center=center,applied_axis=applied_axis,special_kwargs=special_kwargs,**win_kwargs)
    if fill_nans:
        res.fillna(inplace=True,method='ffill')
        res.fillna(inplace=True,method='bfill')
    if return_nans: index = res.index
    else: index = res.notnull()
    if orig_pd_obj: return res[index]
    else: return res[index].values


def reduce_by(data,compared_axis=1,reducer_axis=0,reducer=np.median,percentage = 0.75):
    if data.ndim == 2:
        mask = gen.norm(reducer(data,axis=compared_axis),axis=reducer_axis) > percentage
        ifiltered = np.squeeze(np.argwhere(mask))
        return np.apply_along_axis(lambda x: x[ifiltered],reducer_axis,data)
    elif data.ndim == 3:
        last_dim = 3 - compared_axis - reducer_axis
        mask = np.any((gen.norm(reducer(data,axis=compared_axis)) > percentage),axis=(last_dim - int(last_dim>reducer_axis)))
        ifiltered = np.squeeze(np.argwhere(mask))
        return np.apply_along_axis(lambda x: x[ifiltered],reducer_axis,data)
    else:
        return data


def rms(values,axis=0):
    return np.sqrt((values**2).mean(axis=axis))

