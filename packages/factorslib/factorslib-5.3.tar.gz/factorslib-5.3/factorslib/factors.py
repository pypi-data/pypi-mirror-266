import pandas as pd
import numpy as np
import talib
import pandas_ta as pdta
import ta
import statsmodels.api as sm
from scipy import stats
from sklearn.linear_model import LinearRegression
from tapy import Indicators

pd.set_option('display.max_columns', None)  # 无限制显示数据
pd.set_option('display.max_rows', None)  # 无限制显示数据
pd.set_option('display.float_format', lambda x: '%.5f' % x)  # 禁用科学计数法显示


# --------------------------------------------------------基础，MACD_N1_N2_N3
def talib_MACD(df, target, N1, N2, N3, *args, **kwargs):
    df1 = df.copy()
    df1['MACD_' + str(N1) + '_' + str(N2) + '_' + str(N3)], df1['MACDDEA_' + str(N1) + '_' + str(N2) + '_' + str(N3)], df1['MACDDIFF_' + str(N1) + '_' + str(N2) + '_' + str(N3)] = \
        talib.MACD(target, fastperiod=N1, slowperiod=N2, signalperiod=N3)
    return df1


def pdta_MACD(df, target, N1, N2, N3, *args, **kwargs):
    df1 = pdta.macd(target, fast=N1, slow=N2, signal=N3, talib=False)
    df2 = pd.concat([df, df1], axis=1)
    df2 = df2.rename(columns={'MACDh_' + str(N1) + '_' + str(N2) + '_' + str(N3): 'MACDDIFF_' + str(N1) + '_' + str(N2) + '_' + str(N3)}) \
        .rename(columns={'MACDs_' + str(N1) + '_' + str(N2) + '_' + str(N3): 'MACDDEA_' + str(N1) + '_' + str(N2) + '_' + str(N3)})

    return df2


def ta_MACD(df, target, N1, N2, N3, *args, **kwargs):
    df1 = df.copy()
    df1['MACD_' + str(N1) + '_' + str(N2) + '_' + str(N3)] = ta.trend.macd(target, window_slow=N2, window_fast=N1, fillna=False)
    df1['MACDDEA_' + str(N1) + '_' + str(N2) + '_' + str(N3)] = ta.trend.macd_signal(target, window_slow=N2, window_fast=N1, window_sign=N3, fillna=False)
    df1['MACDDIFF_' + str(N1) + '_' + str(N2) + '_' + str(N3)] = ta.trend.macd_diff(target, window_slow=N2, window_fast=N1, window_sign=N3, fillna=False)
    return df1


# --------------------------------------------------------基础，EMA_N
def talib_EMA(df, target, N, *args, **kwargs):
    df1 = df.copy()
    df1['EMA_' + str(N)] = talib.EMA(target, timeperiod=N)
    return df1


def pdta_EMA(df, target, N, *args, **kwargs):
    df1 = df.copy()
    df1['EMA_' + str(N)] = pdta.ema(target, length=N, talib=False)
    return df1


def ta_EMA(df, target, N, *args, **kwargs):
    df1 = df.copy()
    ema = ta.trend.EMAIndicator(close=target, window=N, fillna=False)
    df1['EMA_' + str(N)] = ema.ema_indicator()
    return df1


# --------------------------------------------------------基础，ROC_N
def talib_ROC(df, target, N, *args, **kwargs):
    df1 = df.copy()
    df1['ROC_' + str(N)] = talib.ROC(target, timeperiod=N)
    return df1


def pdta_ROC(df, target, N, *args, **kwargs):
    df1 = df.copy()
    df1['ROC_' + str(N)] = pdta.roc(close=target, length=N, talib=False)
    return df1


def ta_ROC(df, target, N, *args, **kwargs):
    df1 = df.copy()
    roc = ta.momentum.ROCIndicator(close=target, window=N, fillna=False)
    df1['ROC_' + str(N)] = roc.roc()
    return df1


# --------------------------------------------------------动量，AROONUP_N & AROONDOWN_N & AROONOSC_N
def talib_AROON(df, high, low, N, *args, **kwargs):
    df1 = df.copy()
    df1['AROONDOWN' + '_' + str(N)], df1['AROONUP' + '_' + str(N)] = talib.AROON(high=high, low=low, timeperiod=N)
    return df1


def pdta_ARRON(df, high, low, N, *args, **kwargs):
    df1 = pdta.aroon(high=high, low=low, length=N, talib=False)
    df2 = pd.concat([df, df1], axis=1)
    df2 = df2.rename(columns={'AROOND' + '_' + str(N): 'AROONDOWN' + '_' + str(N)}) \
        .rename(columns={'AROONU' + '_' + str(N): 'AROONUP' + '_' + str(N)})
    return df2


def talib_AROONOSC(df, high, low, N, *args, **kwargs):
    df1 = df.copy()
    df1['AROONOSC' + '_' + str(N)] = talib.AROONOSC(high=high, low=low, timeperiod=N)
    return df1


# --------------------------------------------------------动量，BBIC_N1_N2_N3_N4
def talib_BBIC(df, close, N1, N2, N3, N4, *args, **kwargs):
    df1 = df.copy()
    df1['MA' + '_' + str(N1)] = talib.SMA(close, timeperiod=N1)
    df1['MA' + '_' + str(N2)] = talib.SMA(close, timeperiod=N2)
    df1['MA' + '_' + str(N3)] = talib.SMA(close, timeperiod=N3)
    df1['MA' + '_' + str(N4)] = talib.SMA(close, timeperiod=N4)

    df1['BBI' + '_' + str(N1) + '_' + str(N2) + '_' + str(N3) + '_' + str(N4)] = \
        (df1['MA' + '_' + str(N1)] + df1['MA' + '_' + str(N2)] + df1['MA' + '_' + str(N3)] + df1['MA' + '_' + str(N4)]) / 4

    df1['BBIC' + '_' + str(N1) + '_' + str(N2) + '_' + str(N3) + '_' + str(N4)] = \
        df1['BBI' + '_' + str(N1) + '_' + str(N2) + '_' + str(N3) + '_' + str(N4)] / close

    return df1


def pdta_BBIC(df, close, N1, N2, N3, N4, *args, **kwargs):
    df1 = df.copy()
    df1['MA' + '_' + str(N1)] = pdta.sma(close, length=N1, talib=False)
    df1['MA' + '_' + str(N2)] = pdta.sma(close, length=N2, talib=False)
    df1['MA' + '_' + str(N3)] = pdta.sma(close, length=N3, talib=False)
    df1['MA' + '_' + str(N4)] = pdta.sma(close, length=N4, talib=False)

    df1['BBI' + '_' + str(N1) + '_' + str(N2) + '_' + str(N3) + '_' + str(N4)] = \
        (df1['MA' + '_' + str(N1)] + df1['MA' + '_' + str(N2)] + df1['MA' + '_' + str(N3)] + df1['MA' + '_' + str(N4)]) / 4

    df1['BBIC' + '_' + str(N1) + '_' + str(N2) + '_' + str(N3) + '_' + str(N4)] = \
        df1['BBI' + '_' + str(N1) + '_' + str(N2) + '_' + str(N3) + '_' + str(N4)] / close

    return df1


def ta_BBIC(df, close, N1, N2, N3, N4, *args, **kwargs):
    df1 = df.copy()
    ma1 = ta.trend.SMAIndicator(close=close, window=N1, fillna=False)
    ma2 = ta.trend.SMAIndicator(close=close, window=N2, fillna=False)
    ma3 = ta.trend.SMAIndicator(close=close, window=N3, fillna=False)
    ma4 = ta.trend.SMAIndicator(close=close, window=N4, fillna=False)

    df1['MA' + '_' + str(N1)] = ma1.sma_indicator()
    df1['MA' + '_' + str(N2)] = ma2.sma_indicator()
    df1['MA' + '_' + str(N3)] = ma3.sma_indicator()
    df1['MA' + '_' + str(N4)] = ma4.sma_indicator()

    df1['BBI' + '_' + str(N1) + '_' + str(N2) + '_' + str(N3) + '_' + str(N4)] = \
        (df1['MA' + '_' + str(N1)] + df1['MA' + '_' + str(N2)] + df1['MA' + '_' + str(N3)] + df1['MA' + '_' + str(N4)]) / 4

    df1['BBIC' + '_' + str(N1) + '_' + str(N2) + '_' + str(N3) + '_' + str(N4)] = \
        df1['BBI' + '_' + str(N1) + '_' + str(N2) + '_' + str(N3) + '_' + str(N4)] / close

    return df1


# --------------------------------------------------------动量，BIAS_N
def talib_BIAS(df, close, N, *args, **kwargs):
    df1 = df.copy()
    ma = talib.SMA(close, timeperiod=N)
    df1['BIAS' + '_' + str(N)] = close / ma - 1
    return df1


def pdta_BIAS(df, close, N, *args, **kwargs):
    df1 = pdta.bias(close=close, length=N)
    df2 = pd.concat([df, df1], axis=1)
    df2 = df2.rename(columns={'BIAS_SMA' + '_' + str(N): 'BIAS' + '_' + str(N)})
    return df2


def ta_BIAS(df, close, N, *args, **kwargs):
    df1 = df.copy()
    ma = ta.trend.SMAIndicator(close=close, window=N, fillna=False)
    ma1 = ma.sma_indicator()
    df1['BIAS' + '_' + str(N)] = close / ma1 - 1
    return df1


# --------------------------------------------------------动量，BEARPOWER_N
def talib_BEARPOWER(df, low, close, N, *args, **kwargs):
    df1 = df.copy()
    ema = talib.EMA(close, timeperiod=N)
    df1['BEARPOWER' + '_' + str(N)] = (low - ema) / close
    return df1


def pdta_BEARPOWER(df, low, close, N, *args, **kwargs):
    df1 = df.copy()
    ema = pdta.ema(close, length=N, talib=False)
    df1['BEARPOWER' + '_' + str(N)] = (low - ema) / close
    return df1


def ta_BEARPOWER(df, low, close, N, *args, **kwargs):
    df1 = df.copy()
    ema = ta.trend.EMAIndicator(close=close, window=N, fillna=False)
    ema1 = ema.ema_indicator()
    df1['BEARPOWER' + '_' + str(N)] = (low - ema1) / close
    return df1


# --------------------------------------------------------动量，BULLPOWER_N
def talib_BULLPOWER(df, high, close, N, *args, **kwargs):
    df1 = df.copy()
    ema = talib.EMA(close, timeperiod=N)
    df1['BULLPOWER' + '_' + str(N)] = (high - ema) / close
    return df1


def pdta_BULLPOWER(df, high, close, N, *args, **kwargs):
    df1 = df.copy()
    ema = pdta.ema(close, length=N, talib=False)
    df1['BULLPOWER' + '_' + str(N)] = (high - ema) / close
    return df1


def ta_BULLPOWER(df, high, close, N, *args, **kwargs):
    df1 = df.copy()
    ema = ta.trend.EMAIndicator(close=close, window=N, fillna=False)
    ema1 = ema.ema_indicator()
    df1['BULLPOWER' + '_' + str(N)] = (high - ema1) / close
    return df1


# --------------------------------------------------------动量，CCI_N
def talib_CCI(df, high, low, close, N, *args, **kwargs):
    df1 = df.copy()
    df1['CCI' + '_' + str(N)] = talib.CCI(close=close, high=high, low=low, timeperiod=N)
    return df1


def pdta_CCI(df, high, low, close, N, *args, **kwargs):
    df1 = df.copy()
    df1['CCI' + '_' + str(N)] = pdta.cci(close=close, high=high, low=low, length=N, talib=False)
    return df1


def ta_CCI(df, high, low, close, N, *args, **kwargs):
    df1 = df.copy()
    cci = ta.trend.CCIIndicator(close=close, high=high, low=low, window=N, fillna=False)
    df1['CCI' + '_' + str(N)] = cci.cci()
    return df1


# --------------------------------------------------------动量，CR
def talib_CR(df, high, low, *args, **kwargs):
    df1 = df.copy()
    df1['mprice'] = (high + low) / 2
    df1['upvalue'] = high - df1['mprice'].shift(1)
    df1['downvalue'] = df1['mprice'].shift(1) - low

    df1.loc[df1['upvalue'] < 0, 'upvalue'] = 0
    df1.loc[df1['downvalue'] < 0, 'downvalue'] = 0

    df1['longstrength'] = [df1.loc[i - 25:i, 'upvalue'].sum() for i in range(df1.shape[0])]
    df1['shortstrength'] = [df1.loc[i - 25:i, 'downvalue'].sum() for i in range(df1.shape[0])]

    df1.loc[0:25, 'longstrength'] = np.nan
    df1.loc[0:25, 'shortstrength'] = np.nan

    df1['CR'] = 100 * df1['longstrength'] / df1['shortstrength']

    df1['a'] = talib.SMA(df1['CR'], timeperiod=10).shift(5)
    df1['b'] = talib.SMA(df1['CR'], timeperiod=20).shift(9)
    df1['c'] = talib.SMA(df1['CR'], timeperiod=40).shift(17)
    df1['d'] = talib.SMA(df1['CR'], timeperiod=62).shift(28)

    return df1


def pdta_CR(df, high, low, *args, **kwargs):
    df1 = df.copy()
    df1['mprice'] = (high + low) / 2
    df1['upvalue'] = high - df1['mprice'].shift(1)
    df1['downvalue'] = df1['mprice'].shift(1) - low

    df1.loc[df1['upvalue'] < 0, 'upvalue'] = 0
    df1.loc[df1['downvalue'] < 0, 'downvalue'] = 0

    df1['longstrength'] = [df1.loc[i - 25:i, 'upvalue'].sum() for i in range(df1.shape[0])]
    df1['shortstrength'] = [df1.loc[i - 25:i, 'downvalue'].sum() for i in range(df1.shape[0])]

    df1.loc[0:25, 'longstrength'] = np.nan
    df1.loc[0:25, 'shortstrength'] = np.nan

    df1['CR'] = 100 * df1['longstrength'] / df1['shortstrength']

    df1['a'] = pdta.sma(df1['CR'], length=10, talib=False).shift(5)
    df1['b'] = pdta.sma(df1['CR'], length=20, talib=False).shift(9)
    df1['c'] = pdta.sma(df1['CR'], length=40, talib=False).shift(17)
    df1['d'] = pdta.sma(df1['CR'], length=62, talib=False).shift(28)

    return df1


def ta_CR(df, high, low, *args, **kwargs):
    df1 = df.copy()
    df1['mprice'] = (high + low) / 2
    df1['upvalue'] = high - df1['mprice'].shift(1)
    df1['downvalue'] = df1['mprice'].shift(1) - low

    df1.loc[df1['upvalue'] < 0, 'upvalue'] = 0
    df1.loc[df1['downvalue'] < 0, 'downvalue'] = 0

    df1['longstrength'] = [df1.loc[i - 25:i, 'upvalue'].sum() for i in range(df1.shape[0])]
    df1['shortstrength'] = [df1.loc[i - 25:i, 'downvalue'].sum() for i in range(df1.shape[0])]

    df1.loc[0:25, 'longstrength'] = np.nan
    df1.loc[0:25, 'shortstrength'] = np.nan

    df1['CR'] = 100 * df1['longstrength'] / df1['shortstrength']

    ma1 = ta.trend.SMAIndicator(df1['CR'], window=10, fillna=False)
    ma2 = ta.trend.SMAIndicator(df1['CR'], window=20, fillna=False)
    ma3 = ta.trend.SMAIndicator(df1['CR'], window=40, fillna=False)
    ma4 = ta.trend.SMAIndicator(df1['CR'], window=62, fillna=False)

    df1['a'] = ma1.sma_indicator().shift(5)
    df1['b'] = ma2.sma_indicator().shift(9)
    df1['c'] = ma3.sma_indicator().shift(17)
    df1['d'] = ma4.sma_indicator().shift(28)

    return df1


# --------------------------------------------------------动量，PASTPER_N（当前价格处于过去一段时间价格的位置）
def PASTPER(df, closename, N, *args, **kwargs):
    df1 = df.copy()
    df1['PASTPER_' + str(N)] = [stats.percentileofscore(df1.loc[i - N:i - 1, closename], df1.loc[i, closename], kind='weak') for i in range(df1.shape[0])]
    df1.loc[0:N, 'PASTPER_' + str(N)] = np.nan
    return df1


# --------------------------------------------------------动量，MASS_N1_N2
def talib_MASS(df, high, low, N1, N2, *args, **kwargs):
    df1 = df.copy()
    df1['diff'] = high - low
    df1['ahl'] = talib.EMA(df1['diff'], timeperiod=N1)
    df1['bhl'] = talib.EMA(df1['ahl'], timeperiod=N1)
    df1['ahl/bhl'] = df1['ahl'] / df1['bhl']
    df1['MASS_' + str(N1) + '_' + str(N2)] = [(df1.loc[i - N2 + 1:i, 'ahl/bhl']).sum() for i in range(df1.shape[0])]

    df1.loc[0:N1 + N1 + N2 - 4, 'MASS_' + str(N1) + '_' + str(N2)] = np.nan

    return df1


def pdta_MASS(df, high, low, N1, N2, *args, **kwargs):
    df1 = df.copy()
    df1['MASS_' + str(N1) + '_' + str(N2)] = pdta.massi(high=high, low=low, fast=N1, slow=N2)

    return df1


def ta_MASS(df, high, low, N1, N2, *args, **kwargs):
    df1 = df.copy()
    mass = ta.trend.MassIndex(high=high, low=low, window_fast=N1, window_slow=N2)
    df1['MASS_' + str(N1) + '_' + str(N2)] = mass.mass_index()

    return df1


# --------------------------------------------------------动量，MASSMA_N1_N2_N3
def talib_MASSMA(df, high, low, N1, N2, N3, *args, **kwargs):
    df1 = talib_MASS(df=df, high=high, low=low, N1=N1, N2=N2)
    df1['MASS_' + str(N1) + '_' + str(N2) + '_' + str(N3)] = talib.SMA(df1['MASS_' + str(N1) + '_' + str(N2)], timeperiod=N3)
    return df1


def pdta_MASSMA(df, high, low, N1, N2, N3, *args, **kwargs):
    df1 = pdta_MASS(df=df, high=high, low=low, N1=N1, N2=N2)
    df1['MASS_' + str(N1) + '_' + str(N2) + '_' + str(N3)] = pdta.sma(df1['MASS_' + str(N1) + '_' + str(N2)], length=N3, talib=False)
    return df1


def ta_MASSMA(df, high, low, N1, N2, N3, *args, **kwargs):
    df1 = ta_MASS(df=df, high=high, low=low, N1=N1, N2=N2)
    ma = ta.trend.SMAIndicator(df1['MASS_' + str(N1) + '_' + str(N2)], window=N3, fillna=False)
    df1['MASS_' + str(N1) + '_' + str(N2) + '_' + str(N3)] = ma.sma_indicator()
    return df1


# --------------------------------------------------------动量，PLRC_N
def PLRC(df, closename, timename, N, method, *args, **kwargs):
    if method == 'scipy':
        df1 = df.copy()
        df1[timename] = pd.to_datetime(df1[timename], utc=True)
        for i in range(df.shape[0]):
            if i >= N - 1:
                df1.loc[i, 'PLRC_' + str(N)], df1.loc[i, 'intercept'], df1.loc[i, 'r_value'], df1.loc[i, 'p_value'], df1.loc[i, 'std_err '] = \
                    stats.linregress(x=df1.loc[i - N + 1:i, timename].values.tolist(), y=df1.loc[i - N + 1:i, closename].values.tolist())
            else:
                pass
        return df1

    if method == 'statsmodels':
        df1 = df.copy()
        df1[timename] = pd.to_datetime(df1[timename], utc=True)
        for i in range(df.shape[0]):
            if i >= N - 1:
                model = sm.OLS(df1.loc[i - N + 1:i, closename].values.tolist(), df1.loc[i - N + 1:i, timename].values.tolist()).fit()
                df1.loc[i, 'PLRC_' + str(N)] = model.params
            else:
                pass
        return df1

    if method == 'sklearn':
        df1 = df.copy()
        df1[timename] = pd.to_datetime(df1[timename], utc=True)
        for i in range(df.shape[0]):
            if i >= N - 1:
                x = df1.loc[i - N + 1:i, timename]
                y = df1.loc[i - N + 1:i, closename]
                model = LinearRegression()
                model.fit(x.values.reshape(-1, 1), y)
                df1.loc[i, 'PLRC_' + str(N)] = model.coef_
            else:
                pass
        return df1


# --------------------------------------------------------动量，POVERMEAN_N
def talib_POVERMEAN(df, close, N, *args, **kwargs):
    df1 = df.copy()
    df1['POVERMEAN_' + str(N)] = (close / talib.SMA(close, timeperiod=N)) - 1
    return df1


def pdta_POVERMEAN(df, close, N, *args, **kwargs):
    df1 = df.copy()
    df1['POVERMEAN_' + str(N)] = (close / pdta.sma(close, length=N, talib=False)) - 1
    return df1


def ta_POVERMEAN(df, close, N, *args, **kwargs):
    df1 = df.copy()
    ma = ta.trend.SMAIndicator(close, window=N, fillna=False)
    df1['POVERMEAN_' + str(N)] = (close / ma.sma_indicator()) - 1
    return df1


# --------------------------------------------------------动量，CROC_N
def talib_CROC(df, close, N, *args, **kwargs):
    df1 = talib_ROC(df=df, target=close, N=N)
    df1 = df1.rename(colume={'ROC_' + str(N): 'CROC_' + str(N)})
    return df1


def pdta_CROC(df, close, N, *args, **kwargs):
    df1 = pdta_ROC(df=df, target=close, N=N)
    df1 = df1.rename(colume={'ROC_' + str(N): 'CROC_' + str(N)})
    return df1


def ta_CROC(df, close, N, *args, **kwargs):
    df1 = ta_ROC(df=df, target=close, N=N)
    df1 = df1.rename(colume={'ROC_' + str(N): 'CROC_' + str(N)})
    return df1


# --------------------------------------------------------动量，VPT
def ta_VPT(df, close, volume, *args, **kwargs):
    df1 = df.copy()
    vpt = ta.volume.VolumePriceTrendIndicator(close, volume, fillna=False)
    df1['VPT'] = vpt.volume_price_trend()
    return df1


# --------------------------------------------------------动量，VPTMA_N
def ta_VPTMA(df, close, volume, N, *args, **kwargs):
    df1 = ta_VPT(df=df, close=close, volume=volume)
    ma = ta.trend.SMAIndicator(df1['VPT'], window=N, fillna=False)
    df1['VPTMA_' + str(N)] = ma.sma_indicator()
    return df1


# --------------------------------------------------------动量，TRIX_N
def talib_TRIX(df, close, N, *args, **kwargs):
    df1 = df.copy()
    df1['TRIX_' + str(N)] = talib.TRIX(close, timeperiod=N)
    return df1


def pdta_TRIX(df, close, N1, N2, *args, **kwargs):
    df1 = pdta.trix(close, length=N1, signal=N2)
    df2 = pd.concat([df, df1], axis=1)
    df2 = df2.rename(columns={'TRIX_' + str(N1) + '_' + str(N2): 'TRIX_' + str(N1)}).rename(columns={'TRIXs_' + str(N1) + '_' + str(N2): 'TRIXMA_' + str(N1) + '_' + str(N2)})
    return df2


def ta_TRIX(df, close, N, *args, **kwargs):
    df1 = df.copy()
    trix = ta.trend.TRIXIndicator(close, window=N, fillna=False)
    df1['TRIX_' + str(N)] = trix.trix()
    return df1


# --------------------------------------------------------动量，VOLUMEMP_N
def VOLUMEMP(df, closename, volumename, N, *args, **kwargs):
    df1 = df.copy()
    df1['ret'] = df1[closename] / df1[closename].shift(1) - 1
    df1['VOLUMEMP_' + str(N)] = [(df1.loc[i, volumename] / df1.loc[i - N + 1:i, volumename].mean()) * df1.loc[i - N + 1:i, 'ret'].mean() for i in range(df1.shape[0])]

    df1.loc[0:N - 1, 'VOLUMEMP_' + str(N)] = np.nan

    return df1


# --------------------------------------------------------动量，RETRANK_N
def RETRANK(df, N, symbollist, *args, **kwargs):
    '''
    :param df: pd.Dataframe，BTC_price, ETH_price...
    :param N: int()，多久的排名
    :param symbollist: list[]，BTC，ETH...
    :return:
    '''
    df1 = df.copy()

    df2 = pd.DataFrame()
    for i in list(df1.columns):
        symbol = str(i).split('_')[0]
        df2[symbol + '_ret'] = df1[symbol + '_price'] / df1[symbol + '_price'].shift(N) - 1

    df3 = pd.DataFrame()
    for j in range(df2.shape[0]):
        temp_list = list(df2.loc[j].rank(method="first", ascending=False))
        temp_df = pd.DataFrame([temp_list])
        df3 = pd.concat([df3, temp_df], axis=0)

    df3.columns = [str(i).split('_')[0] + '_rank' for i in list(df1.columns)]

    df2 = df2.reset_index(drop=True)
    df3 = df3.reset_index(drop=True)

    for i in list(df3.columns):
        symbol = str(i).split('_')[0]
        df3[symbol + '_RETRANK_' + str(N)] = (1 - df3[symbol + '_rank']) / len(symbollist)

    df4 = pd.concat([df1, df2], axis=1)
    df4 = pd.concat([df4, df3], axis=1)

    return df4


# --------------------------------------------------------技术，BBANDM_N & BBANDDOWN_N & BBANDUP_N
def talib_BBAND(df, close, N, *args, **kwargs):
    df1 = df.copy()
    df1['BBANDUPPER' + '_' + str(N)], df1['BBANDM' + '_' + str(N)], df1['BBANDLOWER' + '_' + str(N)] = talib.BBANDS(close, timeperiod=N, nbdevup=2, nbdevdn=2, matype=0)
    return df1


def pdta_BBAND(df, close, N, *args, **kwargs):
    df1 = pdta.bbands(close=close, length=N, std=2, talib=False)
    df2 = pd.concat([df, df1], axis=1)
    df2 = df2.rename(columns={'BBL' + '_' + str(N) + '_2.0': 'BBANDLOWER' + '_' + str(N)}) \
        .rename(columns={'BBM' + '_' + str(N) + '_2.0': 'BBANDM' + '_' + str(N)}) \
        .rename(columns={'BBU' + '_' + str(N) + '_2.0': 'BBANDUPPER' + '_' + str(N)}) \
        .rename(columns={'BBB' + '_' + str(N) + '_2.0': 'BBANDWIDTH' + '_' + str(N)}) \
        .rename(columns={'BBP' + '_' + str(N) + '_2.0': 'BBANDPERCENT' + '_' + str(N)})
    return df2


def ta_BBAND(df, close, N, *args, **kwargs):
    df1 = df.copy()
    band1 = ta.volatility.BollingerBands(close, window=N, window_dev=2, fillna=False)
    df1['BBANDM' + '_' + str(N)] = band1.bollinger_mavg()
    df1['BBANDUPPER' + '_' + str(N)] = band1.bollinger_hband()
    df1['BBANDLOWER' + '_' + str(N)] = band1.bollinger_lband()
    return df1


# --------------------------------------------------------技术，EMAC_N
def talib_EMAC(df, close, N, *args, **kwargs):
    df1 = df.copy()
    ema = talib.EMA(close, timeperiod=N)
    df1['EMAC_' + str(N)] = ema / close
    return df1


def pdta_EMAC(df, close, N, *args, **kwargs):
    df1 = df.copy()
    ema = pdta.ema(close, length=N, talib=False)
    df1['EMAC_' + str(N)] = ema / close
    return df1


def ta_EMAC(df, close, N, *args, **kwargs):
    df1 = df.copy()
    ema = ta.trend.EMAIndicator(close, window=N, fillna=False)
    df1['EMAC_' + str(N)] = ema.ema_indicator() / close
    return df1


# --------------------------------------------------------技术，MAC_N
def talib_MAC(df, close, N, *args, **kwargs):
    df1 = df.copy()
    ma = talib.SMA(close, timeperiod=N)
    df1['MAC_' + str(N)] = ma / close
    return df1


def pdta_MAC(df, close, N, *args, **kwargs):
    df1 = df.copy()
    ma = pdta.sma(close, length=N, talib=False)
    df1['MAC_' + str(N)] = ma / close
    return df1


def ta_MAC(df, close, N, *args, **kwargs):
    df1 = df.copy()
    ma = ta.trend.SMAIndicator(close, window=N, fillna=False)
    df1['MAC_' + str(N)] = ma.sma_indicator() / close
    return df1


# --------------------------------------------------------技术，MACDC_N1_N2_N3
def talib_MACDC(df, close, N1, N2, N3, *args, **kwargs):
    df1 = talib_MACD(df=df, target=close, N1=N1, N2=N2, N3=N3)
    df1['MACDC_' + str(N1) + '_' + str(N2) + '_' + str(N3)] = df1['MACD_' + str(N1) + '_' + str(N2) + '_' + str(N3)] / close
    return df1


def pdta_MACDC(df, close, N1, N2, N3, *args, **kwargs):
    df1 = pdta_MACD(df=df, target=close, N1=N1, N2=N2, N3=N3)
    df1['MACDC_' + str(N1) + '_' + str(N2) + '_' + str(N3)] = df1['MACD_' + str(N1) + '_' + str(N2) + '_' + str(N3)] / close
    return df1


def ta_MACDC(df, close, N1, N2, N3, *args, **kwargs):
    df1 = ta_MACD(df=df, target=close, N1=N1, N2=N2, N3=N3)
    df1['MACDC_' + str(N1) + '_' + str(N2) + '_' + str(N3)] = df1['MACD_' + str(N1) + '_' + str(N2) + '_' + str(N3)] / close
    return df1


# --------------------------------------------------------技术，MFI_N
def talib_MFI(df, volume, close, high, low, N, *args, **kwargs):
    df1 = df.copy()
    df1['MFI_' + str(N)] = talib.MFI(volume=volume, close=close, high=high, low=low, timeperiod=N)
    return df1


def pdta_MFI(df, volume, close, high, low, N, *args, **kwargs):
    df1 = df.copy()
    df1['MFI_' + str(N)] = pdta.mfi(volume=volume, close=close, high=high, low=low, length=N, talib=False)
    return df1


def ta_MFI(df, volume, close, high, low, N, *args, **kwargs):
    df1 = df.copy()
    mfi = ta.volume.MFIIndicator(volume=volume, close=close, high=high, low=low, window=N, fillna=False)
    df1['MFI_' + str(N)] = mfi.money_flow_index()
    return df1


# --------------------------------------------------------技术，RSI_N
def talib_RSI(df, close, N, *args, **kwargs):
    df1 = df.copy()
    df1['RSI_' + str(N)] = talib.RSI(close, timeperiod=N)
    return df1


def pdta_RSI(df, close, N, *args, **kwargs):
    df1 = df.copy()
    df1['RSI_' + str(N)] = pdta.rsi(close, length=N, talib=False)
    return df1


def ta_RSI(df, close, N, *args, **kwargs):
    df1 = df.copy()
    rsi = ta.momentum.RSIIndicator(close, window=N, fillna=False)
    df1['RSI_' + str(N)] = rsi.rsi()
    return df1


# --------------------------------------------------------技术，STOCHRSI_N
def pdta_STOCHRSI(df, close, N1, N2, N3, *args, **kwargs):
    df1 = pdta.stochrsi(close, length=N1, rsi_length=N1, k=N2, d=N3, mamode='sma', talib=False)
    df2 = pd.concat([df, df1], axis=1)
    df2 = df2.rename(columns={'STOCHRSIk_' + str(N1) + '_' + str(N1) + '_' + str(N2) + '_' + str(N3): 'STOCHRSIk_' + str(N1) + '_' + str(N2) + '_' + str(N3)}) \
        .rename(columns={'STOCHRSId_' + str(N1) + '_' + str(N1) + '_' + str(N2) + '_' + str(N3): 'STOCHRSId_' + str(N1) + '_' + str(N2) + '_' + str(N3)})
    return df2


def ta_STOCHRSI(df, close, N1, N2, N3, *args, **kwargs):
    df1 = df.copy()
    rsi = ta.momentum.StochRSIIndicator(close, window=N1, smooth1=N2, smooth2=N3, fillna=False)
    df1['STOCHRSI_' + str(N1) + '_' + str(N2) + '_' + str(N3)] = rsi.stochrsi()
    df1['STOCHRSIk_' + str(N1) + '_' + str(N2) + '_' + str(N3)] = rsi.stochrsi_k()
    df1['STOCHRSId_' + str(N1) + '_' + str(N2) + '_' + str(N3)] = rsi.stochrsi_d()
    return df1


# --------------------------------------------------------技术，KDJ_N
def pdta_KDJ(df, close, high, low, N1, N2, *args, **kwargs):
    df1 = pdta.kdj(high=high, low=low, close=close, length=N1, signal=N2)
    df2 = pd.concat([df, df1], axis=1)
    return df2


# --------------------------------------------------------情绪，ARBR_N
def ARBR(df, open, high, low, N, *args, **kwargs):
    '''
    AR and BR is the same in crypto mkt
    '''
    df1 = df.copy()
    df1['hmo'] = high - open
    df1['oml'] = open - low
    df1['AR_' + str(N)] = [(df1.loc[i - N + 1:i, 'hmo'].sum() / df1.loc[i - N + 1:i, 'oml'].sum()) * 100 for i in range(df1.shape[0])]

    df1.loc[0:N - 2, 'AR_' + str(N)] = np.nan

    return df1


# --------------------------------------------------------情绪，ATR_N
def talib_ATR(df, close, high, low, N, *args, **kwargs):
    df1 = df.copy()
    df1['ATR_' + str(N)] = talib.ATR(close=close, high=high, low=low, timeperiod=N)
    return df1


def pdta_ATR(df, close, high, low, N, *args, **kwargs):
    df1 = df.copy()
    df1['ATR_' + str(N)] = pdta.atr(close=close, high=high, low=low, length=N, mamode='sma', talib=False)
    return df1


def ta_ATR(df, close, high, low, N, *args, **kwargs):
    df1 = df.copy()
    atr = ta.volatility.AverageTrueRange(close=close, high=high, low=low, window=N, fillna=False)
    df1['ATR_' + str(N)] = atr.average_true_range()
    return df1


# --------------------------------------------------------情绪，DAVOL_N1_N2
def DAVOL(df, volume, supply, N1, N2, *args, **kwargs):
    df1 = df.copy()
    df1['TURNOVER'] = volume / supply
    df1['TURNOVER_' + str(N1)] = [df1.loc[i - N1 + 1:i, 'TURNOVER'].mean() for i in range(df1.shape[0])]
    df1['TURNOVER_' + str(N2)] = [df1.loc[i - N2 + 1:i, 'TURNOVER'].mean() for i in range(df1.shape[0])]
    df1.loc[0:N2 - 2, 'TURNOVER_' + str(N1)] = np.nan
    df1.loc[0:N2 - 2, 'TURNOVER_' + str(N2)] = np.nan
    df1['DAVOL_' + str(N1) + '_' + str(N2)] = df1['TURNOVER_' + str(N1)] / df1['TURNOVER_' + str(N2)]
    return df1


# --------------------------------------------------------情绪，WVAD_N
def WVAD(df, open, high, low, close, volume, N, *args, **kwargs):
    df1 = df.copy()
    df1['WVAD'] = ((close - open) / (high - low)) * volume
    df1['WVAD_' + str(N)] = [df1.loc[i - N + 1:i, 'WVAD'].sum() for i in range(df1.shape[0])]
    df1.loc[0:N - 2, 'WVAD_' + str(N)] = np.nan
    return df1


# --------------------------------------------------------情绪，MAWVAD_N1_N2
def talib_MAWVAD(df, open, high, low, close, volume, N1, N2, *args, **kwargs):
    df1 = WVAD(df=df, open=open, close=close, high=high, low=low, volume=volume, N=N1)
    df1['MAWVAD_' + str(N1) + '_' + str(N2)] = talib.SMA(df1['WVAD_' + str(N1)], timeperiod=N2)
    return df1


# --------------------------------------------------------情绪，MONEYFLOW_N
def MONEYFLOW(df, close, high, low, volume, N, *args, **kwargs):
    df1 = df.copy()
    df1['MONEYFLOW'] = (close + high + low).mean() * volume
    df1['MONEYFLOW_' + str(N)] = [df1.loc[i - N + 1:i, 'MONEYFLOW'].sum() for i in range(df1.shape[0])]
    df1.loc[0:N - 2, 'MONEYFLOW_' + str(N)] = np.nan
    return df1


# --------------------------------------------------------情绪，PSY_N
def pdta_PSY(df, close, N, *args, **kwargs):
    df1 = df.copy()
    df1['PSY_' + str(N)] = pdta.psl(close=close, length=N)
    return df1


# --------------------------------------------------------情绪，TURNOVERVOL_N
def TURNOVERVOL(df, volume, supply, N, *args, **kwargs):
    df1 = df.copy()
    df1['TURNOVER'] = volume / supply
    df1['TURNOVERVOL_' + str(N)] = [df1.loc[i - N + 1:i, 'TURNOVER'].std() for i in range(df1.shape[0])]
    df1.loc[0:N - 2, 'TURNOVERVOL_' + str(N)] = np.nan
    return df1


# --------------------------------------------------------情绪，TVMA_N
def talib_TVMA(df, quotevolume, N, *args, **kwargs):
    df1 = df.copy()
    df1['TVMA_' + str(N)] = talib.SMA(quotevolume, timeperiod=N)
    return df1


def pdta_TVMA(df, quotevolume, N, *args, **kwargs):
    df1 = df.copy()
    df1['TVMA_' + str(N)] = pdta.sma(quotevolume, length=N, talib=False)
    return df1


def ta_TVMA(df, quotevolume, N, *args, **kwargs):
    df1 = df.copy()
    tvma = ta.trend.SMAIndicator(quotevolume, window=N, fillna=False)
    df1['TVMA_' + str(N)] = tvma.sma_indicator()
    return df1


# --------------------------------------------------------情绪，TVSTD_N
def TVSTD(df, quotevolumename, N, *args, **kwargs):
    df1 = df.copy()
    df1['TVSTD' + str(N)] = [df1.loc[i - N + 1:i, quotevolumename].std() for i in range(df1.shape[0])]
    df1.loc[0:N - 2, 'TVSTD' + str(N)] = np.nan
    return df1


# --------------------------------------------------------情绪，VMACD_N1_N2_N3
def talib_VMACD(df, volume, N1, N2, N3, *args, **kwargs):
    df1 = talib_MACD(df=df, target=volume, N1=N1, N2=N2, N3=N3)
    df1 = df1.rename(columns={'MACD_' + str(N1) + '_' + str(N2) + '_' + str(N3): 'VMACD_' + str(N1) + '_' + str(N2) + '_' + str(N3)}) \
        .rename(columns={'MACDDEA_' + str(N1) + '_' + str(N2) + '_' + str(N3): 'VMACDDEA_' + str(N1) + '_' + str(N2) + '_' + str(N3)}). \
        rename(columns={'MACDDIFF_' + str(N1) + '_' + str(N2) + '_' + str(N3): 'VMACDDIFF_' + str(N1) + '_' + str(N2) + '_' + str(N3)})
    return df1


def pdta_VMACD(df, volume, N1, N2, N3, *args, **kwargs):
    df1 = pdta_MACD(df=df, target=volume, N1=N1, N2=N2, N3=N3)
    df1 = df1.rename(columns={'MACD_' + str(N1) + '_' + str(N2) + '_' + str(N3): 'VMACD_' + str(N1) + '_' + str(N2) + '_' + str(N3)}) \
        .rename(columns={'MACDDEA_' + str(N1) + '_' + str(N2) + '_' + str(N3): 'VMACDDEA_' + str(N1) + '_' + str(N2) + '_' + str(N3)}). \
        rename(columns={'MACDDIFF_' + str(N1) + '_' + str(N2) + '_' + str(N3): 'VMACDDIFF_' + str(N1) + '_' + str(N2) + '_' + str(N3)})
    return df1


def ta_VMACD(df, volume, N1, N2, N3, *args, **kwargs):
    df1 = ta_MACD(df=df, target=volume, N1=N1, N2=N2, N3=N3)
    df1 = df1.rename(columns={'MACD_' + str(N1) + '_' + str(N2) + '_' + str(N3): 'VMACD_' + str(N1) + '_' + str(N2) + '_' + str(N3)}) \
        .rename(columns={'MACDDEA_' + str(N1) + '_' + str(N2) + '_' + str(N3): 'VMACDDEA_' + str(N1) + '_' + str(N2) + '_' + str(N3)}). \
        rename(columns={'MACDDIFF_' + str(N1) + '_' + str(N2) + '_' + str(N3): 'VMACDDIFF_' + str(N1) + '_' + str(N2) + '_' + str(N3)})
    return df1


# --------------------------------------------------------情绪，VEMA_N
def talib_VEMA(df, volume, N, *args, **kwargs):
    df1 = talib_EMA(df=df, target=volume, N=N)
    df1 = df1.rename(columns={'EMA_' + str(N): 'VEMA_' + str(N)})
    return df1


def pdta_VEMA(df, volume, N, *args, **kwargs):
    df1 = pdta_EMA(df=df, target=volume, N=N)
    df1 = df1.rename(columns={'EMA_' + str(N): 'VEMA_' + str(N)})
    return df1


def ta_VEMA(df, volume, N, *args, **kwargs):
    df1 = ta_EMA(df=df, target=volume, N=N)
    df1 = df1.rename(columns={'EMA_' + str(N): 'VEMA_' + str(N)})
    return df1


# --------------------------------------------------------情绪，VOSC_N1_N2
def talib_VOSC(df, volume, N1, N2, *args, **kwargs):
    df1 = talib_EMA(df=df, target=volume, N=N1)
    df1 = df1.rename(columns={'EMA_' + str(N1): 'VEMA_' + str(N1)})
    df2 = talib_EMA(df=df, target=volume, N=N2)
    df2 = df2.rename(columns={'EMA_' + str(N2): 'VEMA_' + str(N2)})
    df3 = pd.concat([df1, df2['VEMA_' + str(N2)]], axis=1)
    df3['VOSC_' + str(N1) + str(N2)] = 100 * (df1['VEMA_' + str(N1)] - df2['VEMA_' + str(N2)]) / df1['VEMA_' + str(N1)]
    return df3


def pdta_VOSC(df, volume, N1, N2, *args, **kwargs):
    df1 = pdta_EMA(df=df, target=volume, N=N1)
    df1 = df1.rename(columns={'EMA_' + str(N1): 'VEMA_' + str(N1)})
    df2 = pdta_EMA(df=df, target=volume, N=N2)
    df2 = df2.rename(columns={'EMA_' + str(N2): 'VEMA_' + str(N2)})
    df3 = pd.concat([df1, df2['VEMA_' + str(N2)]], axis=1)
    df3['VOSC_' + str(N1) + str(N2)] = 100 * (df1['VEMA_' + str(N1)] - df2['VEMA_' + str(N2)]) / df1['VEMA_' + str(N1)]
    return df3


def ta_VOSC(df, volume, N1, N2, *args, **kwargs):
    df1 = ta_EMA(df=df, target=volume, N=N1)
    df1 = df1.rename(columns={'EMA_' + str(N1): 'VEMA_' + str(N1)})
    df2 = ta_EMA(df=df, target=volume, N=N2)
    df2 = df2.rename(columns={'EMA_' + str(N2): 'VEMA_' + str(N2)})
    df3 = pd.concat([df1, df2['VEMA_' + str(N2)]], axis=1)
    df3['VOSC_' + str(N1) + str(N2)] = 100 * (df1['VEMA_' + str(N1)] - df2['VEMA_' + str(N2)]) / df1['VEMA_' + str(N1)]
    return df3


# --------------------------------------------------------情绪，TURNOVERMA_N
def talib_TURNOVERMA(df, volume, supply, N, *args, **kwargs):
    df1 = df.copy()
    df1['TURNOVER'] = volume / supply
    df1['TURNOVERMA_' + str(N)] = talib.SMA(df1['TURNOVER'], timeperiod=N)
    return df1


def pdta_TURNOVERMA(df, volume, supply, N, *args, **kwargs):
    df1 = df.copy()
    df1['TURNOVER'] = volume / supply
    df1['TURNOVERMA_' + str(N)] = pdta.sma(df1['TURNOVER'], length=N, talib=False)
    return df1


def ta_TURNOVERMA(df, volume, supply, N, *args, **kwargs):
    df1 = df.copy()
    df1['TURNOVER'] = volume / supply
    ma = ta.trend.SMAIndicator(df1['TURNOVER'], window=N, fillna=False)
    df1['TURNOVERMA_' + str(N)] = ma.sma_indicator()
    return df1


# --------------------------------------------------------情绪，VR_N
def VR(df, closename, quotevolumename, N, *args, **kwargs):
    df1 = df.copy()
    df1['RET'] = df1[closename] / df1[closename].shift(1) - 1
    df1['AV'] = 0
    df1['BV'] = 0
    df1.loc[df1['RET'] >= 0, 'AV'] = df1[quotevolumename]
    df1.loc[df1['RET'] < 0, 'BV'] = df1[quotevolumename]
    df1['VR_' + str(N)] = [df1.loc[i - N + 1:i, 'AV'].sum() / df1.loc[i - N + 1:i, 'BV'].sum() for i in range(df1.shape[0])]
    df1.loc[0:N - 1, 'VR_' + str(N)] = np.nan
    return df1


# --------------------------------------------------------情绪，VRMA_N1_N2
def talib_VRMA(df, closename, volumename, N1, N2, *args, **kwargs):
    df1 = VR(df=df, closename=closename, volumename=volumename, N=N1)
    df1['VRMA_' + str(N1) + '_' + str(N2)] = talib.SMA(df1['VR_' + str(N1)], timeperiod=N2)
    return df1


def pdta_VRMA(df, closename, volumename, N1, N2, *args, **kwargs):
    df1 = VR(df=df, closename=closename, volumename=volumename, N=N1)
    df1['VRMA_' + str(N1) + '_' + str(N2)] = pdta.sma(df1['VR_' + str(N1)], length=N2, talib=False)
    return df1


def ta_VRMA(df, closename, volumename, N1, N2, *args, **kwargs):
    df1 = VR(df=df, closename=closename, volumename=volumename, N=N1)
    ma = ta.trend.SMAIndicator(df1['VR_' + str(N1)], window=N2, fillna=False)
    df1['VRMA_' + str(N1) + '_' + str(N2)] = ma.sma_indicator()
    return df1


# --------------------------------------------------------情绪，VROC_N
def talib_VROC(df, volume, N, *args, **kwargs):
    df1 = talib_ROC(df=df, target=volume, N=N)
    df1 = df1.rename(columns={'ROC_' + str(N): 'VROC_' + str(N)})
    return df1


def pdta_VROC(df, volume, N, *args, **kwargs):
    df1 = pdta_ROC(df=df, target=volume, N=N)
    df1 = df1.rename(columns={'ROC_' + str(N): 'VROC_' + str(N)})
    return df1


def ta_VROC(df, volume, N, *args, **kwargs):
    df1 = ta_ROC(df=df, target=volume, N=N)
    df1 = df1.rename(columns={'ROC_' + str(N): 'VROC_' + str(N)})
    return df1


# --------------------------------------------------------风险，KURT_N
def KURT(df, targetname, N, *args, **kwargs):
    df1 = df.copy()
    df1['KURT_' + str(N)] = [df1.loc[i - N + 1:i, targetname].kurt() for i in range(df1.shape[0])]
    df1.loc[0:N - 1, 'KURT_' + str(N)] = np.nan
    return df1


# --------------------------------------------------------风险，SKEW_N
def SKEW(df, targetname, N, *args, **kwargs):
    df1 = df.copy()
    df1['SKEW_' + str(N)] = [df1.loc[i - N + 1:i, targetname].skew() for i in range(df1.shape[0])]
    df1.loc[0:N - 1, 'SKEW_' + str(N)] = np.nan
    return df1


# --------------------------------------------------------风险，VARIANCE_N
def VARIANCE(df, targetname, N, *args, **kwargs):
    df1 = df.copy()
    df1['VARIANCE_' + str(N)] = [(df1.loc[i - N + 1:i, targetname].std()) ** 2 for i in range(df1.shape[0])]
    df1.loc[0:N - 1, 'VARIANCE_' + str(N)] = np.nan
    return df1


# --------------------------------------------------------风险，SP_N
def SP(df, N, *args, **kwargs):
    df1 = df.copy()
    df1['ANNRET_' + str(N)] = [((df1.loc[i, 'fundv'] / df1.loc[i - N + 1, 'fundv']) ** (365 / (N - 1))) - 1 for i in range(df1.shape[0])]
    df1['ANNVOL_' + str(N)] = [(df1.loc[i - N + 1:i, 'ANNRET_' + str(N)].std()) * (365 ** 0.5) for i in range(df1.shape[0])]
    df1['SP_' + str(N)] = (df1['ANNRET_' + str(N)] - 0.08) / df1['ANNVOL_' + str(N)]
    df1.loc[0:N - 1, 'ANNRET_' + str(N)] = np.nan
    df1.loc[0:N - 1, 'ANNVOL_' + str(N)] = np.nan
    df1.loc[0:N - 1, 'SP_' + str(N)] = np.nan

    return df1


# --------------------------------------------------------20230608新增，趋势，SAR
def talib_SAR(df, high, low, *args, **kwargs):
    df1 = df.copy()
    df1['SAR'] = talib.SAR(high=high, low=low)
    return df1


def pdta_SAR(df, close, high, low, *args, **kwargs):
    df1 = df.copy()
    df2 = pdta.psar(close=close, high=high, low=low, talib=False)
    df2 = df2.fillna(value=0)
    df2['SAR'] = df2['PSARs_0.02_0.2']
    df2.loc[df2['PSARs_0.02_0.2'] == 0, 'SAR'] = df2['PSARl_0.02_0.2']
    df1['SAR'] = df2['SAR']
    return df1


def ta_SAR(df, close, high, low, *args, **kwargs):
    df1 = df.copy()
    sar = ta.trend.PSARIndicator(close=close, high=high, low=low, fillna=False)
    df1['SAR'] = sar.psar()
    return df1


# --------------------------------------------------------20230608新增，动量，KAMA_N1_N2_N3
def pdta_KAMA(df, close, N1, N2, N3, *args, **kwargs):
    df1 = df.copy()
    df1['KAMA_' + str(N1) + '_' + str(N2) + '_' + str(N3)] = pdta.kama(close=close, length=N1, fast=N2, slow=N3, talib=False)
    return df1


def ta_KAMA(df, close, N1, N2, N3, *args, **kwargs):
    df1 = df.copy()
    kama = ta.momentum.KAMAIndicator(close=close, window=N1, pow1=N2, pow2=N3, fillna=False)
    df1['KAMA_' + str(N1) + '_' + str(N2) + '_' + str(N3)] = kama.kama()
    return df1


# --------------------------------------------------------20230608新增，趋势，ALLIGATOR
def tapy_ALLIGATOR(df, closename, highname, lowname, N1, N2, N3, N4, N5, N6, *args, **kwargs):
    df1 = df.copy()

    df1.rename(columns={closename: 'Close'}).rename(columns={highname: 'High'}).rename(columns={lowname: 'Low'})
    i = Indicators(df1)
    i.alligator(period_jaws=N1, period_teeth=N2, period_lips=N3, shift_jaws=N4, shift_teeth=N5, shift_lips=N6, column_name_jaws='alligator_jaw', column_name_teeth='alligator_teeth', column_name_lips='alligator_lips')
    df2 = i.df

    return df2


# --------------------------------------------------------20230608新增，择时，HAC
def HAC_timing(df, openname, highname, lowname, closename, *args, **kwargs):
    df1 = df.copy()

    df1['hc'] = (df1[openname] + df1[highname] + df1[lowname] + df1[closename]) / 4

    ha_close_values = df1['hc'].values

    length = len(df1)
    haopen = np.zeros(length, dtype=float)
    haopen[0] = (df1[openname][0] + df1[closename][0]) / 2

    for i in range(0, length - 1):
        haopen[i + 1] = (haopen[i] + ha_close_values[i]) / 2
    df1['ho'] = haopen
    df1['hh'] = df1[['ho', 'hc', highname]].max(axis=1)
    df1['hl'] = df1[['ho', 'hc', lowname]].min(axis=1)

    df1['signalF'] = 0
    df1.loc[(df1['hc'] - df1['ho']) >= 0, 'signalF'] = 1

    return df1


def HAC1_timing(df, openname, highname, lowname, closename, N1, N2, N3, N4, MA_df, *args, **kwargs):
    df1 = df.copy()

    df1['hc'] = (df1[openname] + df1[highname] + df1[lowname] + df1[closename]) / 4

    ha_close_values = df1['hc'].values

    length = len(df1)
    haopen = np.zeros(length, dtype=float)
    haopen[0] = (df1[openname][0] + df1[closename][0]) / 2

    for i in range(0, length - 1):
        haopen[i + 1] = (haopen[i] + ha_close_values[i]) / 2
    df1['ho'] = haopen
    df1['hh'] = df1[['ho', 'hc', highname]].max(axis=1)
    df1['hl'] = df1[['ho', 'hc', lowname]].min(axis=1)

    df_final = pd.merge(df1, MA_df, on='time', how='left')

    df_final['signalF'] = 0
    df_final.loc[(df_final['hc'] - df_final['ho'] >= 0) & (df_final['bull'] == 1), 'signalF'] = N1
    df_final.loc[(df_final['hc'] - df_final['ho'] >= 0) & (df_final['bull'] == 0), 'signalF'] = N2
    df_final.loc[(df_final['hc'] - df_final['ho'] < 0) & (df_final['bull'] == 0), 'signalF'] = N3
    df_final.loc[(df_final['hc'] - df_final['ho'] < 0) & (df_final['bull'] == 1), 'signalF'] = N4

    return df_final


def HAC2_timing(df, openname, highname, lowname, closename, N1, *args, **kwargs):
    df1 = df.copy()

    df1['hc'] = (df1[openname] + df1[highname] + df1[lowname] + df1[closename]) / 4

    ha_close_values = df1['hc'].values

    length = len(df1)
    haopen = np.zeros(length, dtype=float)
    haopen[0] = (df1[openname][0] + df1[closename][0]) / 2

    for i in range(0, length - 1):
        haopen[i + 1] = (haopen[i] + ha_close_values[i]) / 2
    df1['ho'] = haopen
    df1['hh'] = df1[['ho', 'hc', highname]].max(axis=1)
    df1['hl'] = df1[['ho', 'hc', lowname]].min(axis=1)

    df1.loc[(df1['hc'] - df1['ho']) >= 0, 'signal'] = 1
    df1.loc[(df1['hc'] - df1['ho']) < 0, 'signal'] = 0

    df1['candle'] = abs(df1['hc'] - df1['ho'])

    df1.loc[df1['signal'] == 1, 'up'] = abs(df1['hh'] - df1['hc'])
    df1.loc[df1['signal'] == 0, 'up'] = abs(df1['hh'] - df1['ho'])

    df1.loc[df1['signal'] == 1, 'down'] = abs(df1['hl'] - df1['ho'])
    df1.loc[df1['signal'] == 0, 'down'] = abs(df1['hl'] - df1['hc'])

    df1['candleMA'] = talib.SMA(df1['candle'], timeperiod=N1)
    df1['upMA'] = talib.SMA(df1['up'], timeperiod=N1)
    df1['downMA'] = talib.SMA(df1['down'], timeperiod=N1)

    # 判定反转
    df1['signalRev'] = df1['signal']
    df1.loc[(df1['signal'] == 1) & (df1['candle'] < df1['candleMA']) & (df1['up'] < df1['upMA']) & (df1['down'] > df1['downMA']), 'signalRev'] = 0
    df1.loc[(df1['signal'] == 0) & (df1['candle'] < df1['candleMA']) & (df1['up'] > df1['upMA']) & (df1['down'] < df1['downMA']), 'signalRev'] = 1

    df1['signalF'] = df1['signalRev']

    return df1


def HAC3_timing(df, openname, highname, lowname, closename, N1, N2, N3, N4, N5, MA_df, *args, **kwargs):
    df1 = df.copy()

    df1['hc'] = (df1[openname] + df1[highname] + df1[lowname] + df1[closename]) / 4

    ha_close_values = df1['hc'].values

    length = len(df1)
    haopen = np.zeros(length, dtype=float)
    haopen[0] = (df1[openname][0] + df1[closename][0]) / 2

    for i in range(0, length - 1):
        haopen[i + 1] = (haopen[i] + ha_close_values[i]) / 2
    df1['ho'] = haopen
    df1['hh'] = df1[['ho', 'hc', highname]].max(axis=1)
    df1['hl'] = df1[['ho', 'hc', lowname]].min(axis=1)

    df1.loc[(df1['hc'] - df1['ho']) >= 0, 'signal'] = 1
    df1.loc[(df1['hc'] - df1['ho']) < 0, 'signal'] = 0

    df1['candle'] = abs(df1['hc'] - df1['ho'])

    df1.loc[df1['signal'] == 1, 'up'] = abs(df1['hh'] - df1['hc'])
    df1.loc[df1['signal'] == 0, 'up'] = abs(df1['hh'] - df1['ho'])

    df1.loc[df1['signal'] == 1, 'down'] = abs(df1['hl'] - df1['ho'])
    df1.loc[df1['signal'] == 0, 'down'] = abs(df1['hl'] - df1['hc'])

    df1['candleMA'] = talib.SMA(df1['candle'], timeperiod=N1)
    df1['upMA'] = talib.SMA(df1['up'], timeperiod=N1)
    df1['downMA'] = talib.SMA(df1['down'], timeperiod=N1)

    # 判定反转
    df1['signalRev'] = df1['signal']
    df1.loc[(df1['signal'] == 1) & (df1['candle'] < df1['candleMA']) & (df1['up'] < df1['upMA']) & (df1['down'] > df1['downMA']), 'signalRev'] = 0
    df1.loc[(df1['signal'] == 0) & (df1['candle'] < df1['candleMA']) & (df1['up'] > df1['upMA']) & (df1['down'] < df1['downMA']), 'signalRev'] = 1

    df_final = pd.merge(df1, MA_df, on='time', how='left')

    df_final['signalF'] = 0
    df_final.loc[(df_final['signalRev'] == 1) & (df_final['bull'] == 1), 'signalF'] = N2
    df_final.loc[(df_final['signalRev'] == 1) & (df_final['bull'] == 0), 'signalF'] = N3
    df_final.loc[(df_final['signalRev'] == 0) & (df_final['bull'] == 0), 'signalF'] = N4
    df_final.loc[(df_final['signalRev'] == 0) & (df_final['bull'] == 1), 'signalF'] = N5

    return df_final


# --------------------------------------------------------20230608新增，择时，RSI
def RSI_timing(df, close, N1, N2, *args, **kwargs):
    df1 = df.copy()
    df1['time'] = pd.to_datetime(df1['time'], utc=True)
    df1['RSI'] = talib.RSI(close, timeperiod=N1)
    df1['RSIMA'] = talib.SMA(df1['RSI'], timeperiod=N2)

    df1['signalF'] = 0
    df1.loc[df1['RSI'] >= df1['RSIMA'], 'signalF'] = 1

    return df1


def RSI1_timing(df, close, N1, N2, *args, **kwargs):
    df1 = df.copy()
    df1['time'] = pd.to_datetime(df1['time'], utc=True)
    df1['RSI1'] = talib.RSI(close, timeperiod=N1)
    df1['RSI2'] = talib.RSI(close, timeperiod=N2)

    df1['signalF'] = 0
    df1.loc[df1['RSI1'] >= df1['RSI2'], 'signalF'] = 1

    return df1


def RSI2_timing(df, close, N1, N2, N3, N4, MA_df, *args, **kwargs):
    df1 = df.copy()
    df1['time'] = pd.to_datetime(df1['time'], utc=True)
    df1['RSI'] = talib.RSI(close, timeperiod=N1)
    df1['RSIMA'] = talib.SMA(df1['RSI'], timeperiod=N2)

    df1['signal'] = 0
    df1.loc[df1['RSI'] >= df1['RSIMA'], 'signal'] = 1

    df_final = pd.merge(df1, MA_df, on='time', how='left')
    df_final['bull'].fillna(method='ffill', inplace=True)

    df_final['signalF'] = 0
    df_final.loc[(df_final['signal'] == 1) & (df_final['bull'] == 1), 'signalF'] = N3
    df_final.loc[(df_final['signal'] == 1) & (df_final['bull'] == 0), 'signalF'] = N4

    return df_final


# --------------------------------------------------------20230608新增，择时，BBAND
def BBAND_timing(df, close, N1, N2, *args, **kwargs):
    df1 = df.copy()
    df1['time'] = pd.to_datetime(df1['time'], utc=True)

    df1['BBANDU'], df1['BBANDM'], df1['BBANDL'] = talib.BBANDS(close, timeperiod=N1, nbdevup=2, nbdevdn=2, matype=0)

    df1['signalF'] = 0
    df1.loc[close > df1['BBANDM'], 'signalF'] = 1

    return df1


def BBAND1_timing(df, close, N1, N2, N3, N4, N5, MA_df, *args, **kwargs):
    df1 = df.copy()
    df1['time'] = pd.to_datetime(df1['time'], utc=True)

    df1['BBANDU'], df1['BBANDM'], df1['BBANDL'] = talib.BBANDS(close, timeperiod=N1, nbdevup=2, nbdevdn=2, matype=0)

    df2 = pd.merge(df1, MA_df, on='time', how='left')

    df2['signalF'] = 0
    df2.loc[(close > df2['BBANDM']) & (df2['bull'] == 1), 'signalF'] = N2
    df2.loc[(close > df2['BBANDM']) & (df2['bull'] == 0), 'signalF'] = N3
    df2.loc[(close > df2['BBANDU']) & (df2['bull'] == 0), 'signalF'] = N4
    df2.loc[(close > df2['BBANDU']) & (df2['bull'] == 1), 'signalF'] = N5

    return df2


# --------------------------------------------------------20230608新增，择时，EMA
def EMA_timing(df, close, N1, N2, *args, **kwargs):
    df1 = df.copy()
    df1['time'] = pd.to_datetime(df1['time'], utc=True)

    df1['EMA1'] = talib.EMA(close, timeperiod=N1)
    df1['EMA2'] = talib.EMA(close, timeperiod=N2)

    df1['signalF'] = 0
    df1.loc[(close > df1['EMA1']) & (df1['EMA1'] > df1['EMA2']), 'signalF'] = 1
    df1.loc[(close < df1['EMA1']) & (df1['EMA1'] < df1['EMA2']), 'signalF'] = 0

    return df1


# --------------------------------------------------------20230608新增，择时，MACD
def MACD_timing(df, close, N1, N2, N3, *args, **kwargs):
    df1 = df.copy()
    df1['time'] = pd.to_datetime(df1['time'], utc=True)

    df1 = talib_MACD(df=df1, target=close, N1=N1, N2=N2, N3=N3)

    df1['signalF'] = 0
    df1.loc[df1['MACD_' + str(N1) + '_' + str(N2) + '_' + str(N3)] > 0, 'signalF'] = 1

    return df1


def MACD1_timing(df, close, N1, N2, N3, N4, *args, **kwargs):
    df1 = df.copy()
    df1['time'] = pd.to_datetime(df1['time'], utc=True)

    df1 = talib_MACD(df=df1, target=close, N1=N1, N2=N2, N3=N3)
    df1['MACDMA'] = talib.SMA(df1['MACD_' + str(N1) + '_' + str(N2) + '_' + str(N3)], timeperiod=N4)

    df1['signalF'] = 0
    df1.loc[df1['MACD_' + str(N1) + '_' + str(N2) + '_' + str(N3)] > 0, 'signalF'] = 1
    df1.loc[df1['MACD_' + str(N1) + '_' + str(N2) + '_' + str(N3)] < df1['MACDMA'], 'signalF'] = 0

    return df1


def MACD2_timing(df, close, N1, N2, N3, N4, N5, N6, MA_df, *args, **kwargs):
    df1 = df.copy()
    df1['time'] = pd.to_datetime(df1['time'], utc=True)

    df1 = talib_MACD(df=df1, target=close, N1=N1, N2=N2, N3=N3)
    df1['MACDMA'] = talib.SMA(df1['MACD_' + str(N1) + '_' + str(N2) + '_' + str(N3)], timeperiod=N4)

    df_final = pd.merge(df1, MA_df, on='time', how='left')
    df_final['bull'].fillna(method='ffill', inplace=True)

    df_final['signalF'] = 0
    df_final.loc[(df_final['MACD_' + str(N1) + '_' + str(N2) + '_' + str(N3)] > 0) & (df_final['bull'] == 1), 'signalF'] = N5
    df_final.loc[(df_final['MACD_' + str(N1) + '_' + str(N2) + '_' + str(N3)] > 0) & (df_final['bull'] == 0), 'signalF'] = N6
    df_final.loc[df_final['MACD_' + str(N1) + '_' + str(N2) + '_' + str(N3)] < df_final['MACDMA'], 'signalF'] = 0

    return df_final


def MACD3_timing(df, close, N1, N2, N3, N4, N5, *args, **kwargs):
    df1 = df.copy()
    df1['time'] = pd.to_datetime(df1['time'], utc=True)

    df1 = talib_MACD(df=df1, target=close, N1=N1, N2=N2, N3=N3)
    df1['MACDMA1'] = talib.SMA(df1['MACD_' + str(N1) + '_' + str(N2) + '_' + str(N3)], timeperiod=N4)
    df1['MACDMA2'] = talib.SMA(df1['MACD_' + str(N1) + '_' + str(N2) + '_' + str(N3)], timeperiod=N5)

    df1['signalF'] = 0
    df1.loc[df1['MACD_' + str(N1) + '_' + str(N2) + '_' + str(N3)] > 0, 'signalF'] = 1
    df1.loc[(df1['MACD_' + str(N1) + '_' + str(N2) + '_' + str(N3)] < 0) & (df1['MACD_' + str(N1) + '_' + str(N2) + '_' + str(N3)] > df1['MACDMA2']), 'signalF'] = 1

    df1.loc[df1['MACD_' + str(N1) + '_' + str(N2) + '_' + str(N3)] < df1['MACDMA1'], 'signalF'] = 0

    return df1


def MACD4_timing(df, close, N1, N2, N3, N4, N5, N6, N7, N8, N9, MA_df, *args, **kwargs):
    df1 = df.copy()
    df1['time'] = pd.to_datetime(df1['time'], utc=True)

    df1 = talib_MACD(df=df1, target=close, N1=N1, N2=N2, N3=N3)
    df1['MACDMA1'] = talib.SMA(df1['MACD_' + str(N1) + '_' + str(N2) + '_' + str(N3)], timeperiod=N4)
    df1['MACDMA2'] = talib.SMA(df1['MACD_' + str(N1) + '_' + str(N2) + '_' + str(N3)], timeperiod=N5)

    df_final = pd.merge(df1, MA_df, on='time', how='left')
    df_final['bull'].fillna(method='ffill', inplace=True)

    df_final['signalF'] = 0
    df_final.loc[(df_final['MACD_' + str(N1) + '_' + str(N2) + '_' + str(N3)] > 0) & (df_final['bull'] == 1), 'signalF'] = N6
    df_final.loc[(df_final['MACD_' + str(N1) + '_' + str(N2) + '_' + str(N3)] > 0) & (df_final['bull'] == 0), 'signalF'] = N7

    df_final.loc[(df_final['MACD_' + str(N1) + '_' + str(N2) + '_' + str(N3)] < 0) & (df_final['MACD_' + str(N1) + '_' + str(N2) + '_' + str(N3)] > df_final['MACDMA2']) & (df_final['bull'] == 1), 'signalF'] = N8
    df_final.loc[(df_final['MACD_' + str(N1) + '_' + str(N2) + '_' + str(N3)] < 0) & (df_final['MACD_' + str(N1) + '_' + str(N2) + '_' + str(N3)] > df_final['MACDMA2']) & (df_final['bull'] == 0), 'signalF'] = N9

    df_final.loc[df_final['MACD_' + str(N1) + '_' + str(N2) + '_' + str(N3)] < df_final['MACDMA1'], 'signalF'] = 0

    return df_final


# --------------------------------------------------------20230608新增，择时，KDJ
def KDJ_timing(df, close, high, low, N1, N2, *args, **kwargs):
    df1 = df.copy()
    df1['time'] = pd.to_datetime(df1['time'], utc=True)

    df1 = pdta.kdj(high=high, low=low, close=close, length=N1, signal=N2)
    df1.columns = ['K', 'D', 'J']
    df2 = pd.concat([df, df1], axis=1)

    df2['signalF'] = 0
    df2.loc[df2['K'] > df2['D'], 'signalF'] = 1

    return df2


def KDJ1_timing(df, close, high, low, N1, N2, N3, *args, **kwargs):
    df1 = df.copy()
    df1['time'] = pd.to_datetime(df1['time'], utc=True)

    df1 = pdta.kdj(high=high, low=low, close=close, length=N1, signal=N2)
    df1.columns = ['K', 'D', 'J']
    df2 = pd.concat([df, df1], axis=1)

    df2['KMA'] = talib.SMA(df2['K'], timeperiod=N3)

    df2['signalF'] = 0
    df2.loc[df2['K'] > df2['D'], 'signalF'] = 1
    df2.loc[df2['K'] < df2['KMA'], 'signalF'] = 0

    return df2


def KDJ2_timing(df, close, high, low, N1, N2, N3, N4, *args, **kwargs):

    df1 = df.copy()
    df1['time'] = pd.to_datetime(df1['time'], utc=True)

    df1 = pdta.kdj(high=high, low=low, close=close, length=N1, signal=N2)
    df1.columns = ['K', 'D', 'J']
    df2 = pd.concat([df, df1], axis=1)

    df2['KMA'] = talib.SMA(df2['K'], timeperiod=N3)

    df2['signalF'] = 0
    df2.loc[df2['K'] > df2['D'], 'signalF'] = 1
    df2.loc[df2['K'] < df2['KMA'], 'signalF'] = 0
    df2.loc[(df2['K'] > N4) & (df2['D'] > N4), 'signalF'] = 0

    return df2


def KDJ3_timing(df, close, high, low, N1, N2, N3, N4, MA_df, *args, **kwargs):
    df1 = df.copy()
    df1['time'] = pd.to_datetime(df1['time'], utc=True)

    df1 = pdta.kdj(high=high, low=low, close=close, length=N1, signal=N2)
    df1.columns = ['K', 'D', 'J']
    df2 = pd.concat([df, df1], axis=1)

    df_final = pd.merge(df2, MA_df, on='time', how='left')
    df_final['bull'].fillna(method='ffill', inplace=True)

    df_final['signalF'] = 0
    df_final.loc[(df_final['K'] > df_final['D']) & (df_final['bull'] == 1), 'signalF'] = N3
    df_final.loc[(df_final['K'] > df_final['D']) & (df_final['bull'] == 0), 'signalF'] = N4

    return df_final


def KDJ4_timing(df, close, high, low, N1, N2, N3, N4, N5, MA_df, *args, **kwargs):
    df1 = df.copy()
    df1['time'] = pd.to_datetime(df1['time'], utc=True)

    df1 = pdta.kdj(high=high, low=low, close=close, length=N1, signal=N2)
    df1.columns = ['K', 'D', 'J']
    df2 = pd.concat([df, df1], axis=1)

    df2['KMA'] = talib.SMA(df2['K'], timeperiod=N3)

    df_final = pd.merge(df2, MA_df, on='time', how='left')
    df_final['bull'].fillna(method='ffill', inplace=True)

    df_final['signalF'] = 0
    df_final.loc[(df_final['K'] > df_final['D']) & (df_final['bull'] == 1), 'signalF'] = N4
    df_final.loc[(df_final['K'] > df_final['D']) & (df_final['bull'] == 0), 'signalF'] = N5

    df_final.loc[df2['K'] < df_final['KMA'], 'signalF'] = 0

    return df_final


# --------------------------------------------------------20230608新增，择时，STOCHRSI，useless
def STOCHRSI_timing(df, close, N1, N2, N3, N4, *args, **kwargs):
    df1 = df.copy()
    df1['time'] = pd.to_datetime(df1['time'], utc=True)

    df1 = pdta.stochrsi(close, length=N1, rsi_length=N2, k=N3, d=N4, mamode='sma', talib=False)
    df1.columns = ['STOCHRSIK', 'STOCHRSID']
    df2 = pd.concat([df, df1], axis=1)

    df2['signalF'] = 0
    df2.loc[df2['STOCHRSIK'] > 80, 'signalF'] = 1

    return df2


def STOCHRSI1_timing(df, close, N1, N2, N3, N4, N5, N6, MA_df, *args, **kwargs):
    df1 = df.copy()
    df1['time'] = pd.to_datetime(df1['time'], utc=True)

    df1 = pdta.stochrsi(close, length=N1, rsi_length=N2, k=N3, d=N4, mamode='sma', talib=False)
    df1.columns = ['STOCHRSIK', 'STOCHRSID']
    df2 = pd.concat([df, df1], axis=1)

    df_final = pd.merge(df2, MA_df, on='time', how='left')
    df_final['bull'].fillna(method='ffill', inplace=True)

    df_final['signalF'] = 0
    df_final.loc[(df_final['STOCHRSIK'] > df_final['STOCHRSID']) & (df_final['bull'] == 1), 'signalF'] = N5
    df_final.loc[(df_final['STOCHRSIK'] > df_final['STOCHRSID']) & (df_final['bull'] == 0), 'signalF'] = N6

    return df_final


# --------------------------------------------------------20230608新增，择时，ALLIGATOR
def ALLIGATOR_timing(df, closename, highname, lowname, N1, N2, N3, N4, N5, N6, *args, **kwargs):
    df1 = df.copy()
    df1['time'] = pd.to_datetime(df1['time'], utc=True)

    df1 = df1.rename(columns={closename: 'Close'}).rename(columns={highname: 'High'}).rename(columns={lowname: 'Low'})
    i = Indicators(df1)
    i.alligator(period_jaws=N1, period_teeth=N2, period_lips=N3, shift_jaws=N4, shift_teeth=N5, shift_lips=N6, column_name_jaws='alligator_jaw', column_name_teeth='alligator_teeth', column_name_lips='alligator_lips')
    df2 = i.df

    df2['signalF'] = 0
    df2.loc[(df2['Close'] > df2['alligator_jaw'])
            & (df2['Close'] > df2['alligator_teeth'])
            & (df2['Close'] > df2['alligator_lips']), 'signalF'] = 1

    df2 = df2.rename(columns={'Close': closename}).rename(columns={highname: 'High'}).rename(
        columns={'Low': lowname})

    return df2


def ALLIGATOR1_timing(df, closename, highname, lowname, N1, N2, N3, N4, N5, N6, N7, N8, MA_df, *args, **kwargs):
    df1 = df.copy()
    df1['time'] = pd.to_datetime(df1['time'], utc=True)

    df1 = df1.rename(columns={closename: 'Close'}).rename(columns={highname: 'High'}).rename(columns={lowname: 'Low'})
    i = Indicators(df1)
    i.alligator(period_jaws=N1, period_teeth=N2, period_lips=N3, shift_jaws=N4, shift_teeth=N5, shift_lips=N6,
                column_name_jaws='alligator_jaw', column_name_teeth='alligator_teeth',
                column_name_lips='alligator_lips')
    df2 = i.df

    df_final = pd.merge(df2, MA_df, on='time', how='left')
    df_final['bull'].fillna(method='ffill', inplace=True)

    df_final['signalF'] = 0
    df_final.loc[(df_final['Close'] > df_final['alligator_jaw'])
                 & (df_final['Close'] > df_final['alligator_teeth'])
                 & (df_final['Close'] > df_final['alligator_lips']) & (df_final['bull'] == 1), 'signalF'] = N7

    df_final.loc[(df_final['Close'] > df_final['alligator_jaw'])
                 & (df_final['Close'] > df_final['alligator_teeth'])
                 & (df_final['Close'] > df_final['alligator_lips']) & (df_final['bull'] == 0), 'signalF'] = N8

    df_final = df_final.rename(columns={'Close': closename}).rename(columns={highname: 'High'}).rename(
        columns={'Low': lowname})

    return df_final


def ALLIGATOR2_timing(df, closename, highname, lowname, N1, N2, N3, N4, N5, N6, N7, *args, **kwargs):
    df1 = df.copy()
    df1['time'] = pd.to_datetime(df1['time'], utc=True)

    df1 = df1.rename(columns={closename: 'Close'}).rename(columns={highname: 'High'}).rename(columns={lowname: 'Low'})
    i = Indicators(df1)
    i.alligator(period_jaws=N1, period_teeth=N2, period_lips=N3, shift_jaws=N4, shift_teeth=N5, shift_lips=N6, column_name_jaws='alligator_jaw', column_name_teeth='alligator_teeth', column_name_lips='alligator_lips')
    df2 = i.df

    df2['diff'] = (abs(df2['alligator_jaw'] - df2['alligator_teeth']) + abs(df2['alligator_jaw'] - df2['alligator_lips']) + abs(df2['alligator_teeth'] - df2['alligator_lips'])) / 3
    df2['diffMA'] = talib.SMA(df2['diff'], timeperiod=N7)

    df2['signalF'] = 0
    df2.loc[(df2['Close'] > df2['alligator_jaw'])
            & (df2['Close'] > df2['alligator_teeth'])
            & (df2['Close'] > df2['alligator_lips']), 'signalF'] = 1

    df2.loc[df2['diff'] < df2['diffMA'], 'signalF'] = 0

    df2 = df2.rename(columns={'Close': closename}).rename(columns={highname: 'High'}).rename(
        columns={'Low': lowname})

    return df2


def ALLIGATOR3_timing(df, closename, highname, lowname, N1, N2, N3, N4, N5, N6, N7, *args, **kwargs):
    df1 = df.copy()
    df1['time'] = pd.to_datetime(df1['time'], utc=True)

    df1 = df1.rename(columns={closename: 'Close'}).rename(columns={highname: 'High'}).rename(columns={lowname: 'Low'})
    i = Indicators(df1)
    i.alligator(period_jaws=N1, period_teeth=N2, period_lips=N3, shift_jaws=N4, shift_teeth=N5, shift_lips=N6, column_name_jaws='alligator_jaw', column_name_teeth='alligator_teeth', column_name_lips='alligator_lips')
    df2 = i.df

    df2['diff'] = (abs(df2['alligator_jaw'] - df2['alligator_teeth']) + abs(df2['alligator_jaw'] - df2['alligator_lips']) + abs(df2['alligator_teeth'] - df2['alligator_lips'])) / 3
    df2['diffMA'] = talib.SMA(df2['diff'], timeperiod=N7)

    df2['signalF'] = 0
    df2.loc[df2['Close'] > df2['alligator_jaw'], 'signalF'] = 1
    df2.loc[df2['diff'] < df2['diffMA'], 'signalF'] = 0

    df2 = df2.rename(columns={'Close': closename}).rename(columns={highname: 'High'}).rename(
        columns={'Low': lowname})

    return df2


def ALLIGATOR4_timing(df, closename, highname, lowname, N1, N2, N3, N4, N5, N6, N7, N8, N9, MA_df, *args, **kwargs):
    df1 = df.copy()
    df1['time'] = pd.to_datetime(df1['time'], utc=True)

    df1 = df1.rename(columns={closename: 'Close'}).rename(columns={highname: 'High'}).rename(columns={lowname: 'Low'})
    i = Indicators(df1)
    i.alligator(period_jaws=N1, period_teeth=N2, period_lips=N3, shift_jaws=N4, shift_teeth=N5, shift_lips=N6, column_name_jaws='alligator_jaw', column_name_teeth='alligator_teeth', column_name_lips='alligator_lips')
    df2 = i.df

    df2['diff'] = (abs(df2['alligator_jaw'] - df2['alligator_teeth']) + abs(df2['alligator_jaw'] - df2['alligator_lips']) + abs(df2['alligator_teeth'] - df2['alligator_lips'])) / 3
    df2['diffMA'] = talib.SMA(df2['diff'], timeperiod=N7)

    df_final = pd.merge(df2, MA_df, on='time', how='left')
    df_final['bull'].fillna(method='ffill', inplace=True)

    df_final['signalF'] = 0
    df_final.loc[(df_final['Close'] > df_final['alligator_jaw'])
                 & (df_final['Close'] > df_final['alligator_teeth'])
                 & (df_final['Close'] > df_final['alligator_lips']) & (df_final['bull'] == 1), 'signalF'] = N8
    df_final.loc[(df_final['Close'] > df_final['alligator_jaw'])
                 & (df_final['Close'] > df_final['alligator_teeth'])
                 & (df_final['Close'] > df_final['alligator_lips']) & (df_final['bull'] == 0), 'signalF'] = N9

    df_final.loc[df_final['diff'] < df_final['diffMA'], 'signalF'] = 0

    df_final = df_final.rename(columns={'Close': closename}).rename(columns={highname: 'High'}).rename(
        columns={'Low': lowname})

    return df_final


# --------------------------------------------------------20230608新增，择时，BBI
def BBIC_timing(df, close, N1, N2, N3, N4, *args, **kwargs):
    df1 = df.copy()
    df1['time'] = pd.to_datetime(df1['time'], utc=True)
    ma1 = ta.trend.SMAIndicator(close=close, window=N1, fillna=False)
    ma2 = ta.trend.SMAIndicator(close=close, window=N2, fillna=False)
    ma3 = ta.trend.SMAIndicator(close=close, window=N3, fillna=False)
    ma4 = ta.trend.SMAIndicator(close=close, window=N4, fillna=False)

    df1['MA' + '_' + str(N1)] = ma1.sma_indicator()
    df1['MA' + '_' + str(N2)] = ma2.sma_indicator()
    df1['MA' + '_' + str(N3)] = ma3.sma_indicator()
    df1['MA' + '_' + str(N4)] = ma4.sma_indicator()

    df1['BBI'] = (df1['MA' + '_' + str(N1)] + df1['MA' + '_' + str(N2)] + df1['MA' + '_' + str(N3)] + df1['MA' + '_' + str(N4)]) / 4
    df1['BBIC'] = df1['BBI'] / close

    df1['signalF'] = 0
    df1.loc[close > df1['BBI'], 'signalF'] = 1

    return df1


def BBIC1_timing(df, close, N1, N2, N3, N4, N5, N6, MA_df, *args, **kwargs):
    df1 = df.copy()
    df1['time'] = pd.to_datetime(df1['time'], utc=True)
    ma1 = ta.trend.SMAIndicator(close=close, window=N1, fillna=False)
    ma2 = ta.trend.SMAIndicator(close=close, window=N2, fillna=False)
    ma3 = ta.trend.SMAIndicator(close=close, window=N3, fillna=False)
    ma4 = ta.trend.SMAIndicator(close=close, window=N4, fillna=False)

    df1['MA' + '_' + str(N1)] = ma1.sma_indicator()
    df1['MA' + '_' + str(N2)] = ma2.sma_indicator()
    df1['MA' + '_' + str(N3)] = ma3.sma_indicator()
    df1['MA' + '_' + str(N4)] = ma4.sma_indicator()

    df1['BBI'] = (df1['MA' + '_' + str(N1)] + df1['MA' + '_' + str(N2)] + df1['MA' + '_' + str(N3)] + df1['MA' + '_' + str(N4)]) / 4
    df1['BBIC'] = df1['BBI'] / close

    df_final = pd.merge(df1, MA_df, on='time', how='left')
    df_final['bull'].fillna(method='ffill', inplace=True)

    df_final['signalF'] = 0
    df_final.loc[(close > df_final['BBI']) & (df_final['bull'] == 1), 'signalF'] = N5
    df_final.loc[(close > df_final['BBI']) & (df_final['bull'] == 0), 'signalF'] = N6

    return df_final


# --------------------------------------------------------20230608新增，择时，ICHIMOKU
def ICHIMOKU_timing(df, close, high, low, N1, N2, N3, *args, **kwargs):
    df1 = df.copy()
    df1['time'] = pd.to_datetime(df1['time'], utc=True)

    df2, df3 = pdta.ichimoku(close=close, high=high, low=low, tenkan=N1, kijun=N2, senkou=N3, talib=False)
    df_final = pd.concat([df1, df2], axis=1)

    df_final['signalF'] = 0
    df_final.loc[df_final['ITS_' + str(N1)] > df_final['IKS_' + str(N2)], 'signalF'] = 1

    return df_final


def ICHIMOKU1_timing(df, close, high, low, N1, N2, N3, *args, **kwargs):
    df1 = df.copy()
    df1['time'] = pd.to_datetime(df1['time'], utc=True)

    df2, df3 = pdta.ichimoku(close=close, high=high, low=low, tenkan=N1, kijun=N2, senkou=N3, talib=False)
    df_final = pd.concat([df1, df2], axis=1)

    df_final['signalF'] = 0
    df_final.loc[df_final['ITS_' + str(N1)] > df_final['IKS_' + str(N2)], 'signalF'] = 1
    df_final.loc[df_final['ISB_' + str(N2)] > df_final['ISA_' + str(N1)], 'signalF'] = 0

    return df_final


def ICHIMOKU2_timing(df, close, high, low, N1, N2, N3, *args, **kwargs):
    df1 = df.copy()
    df1['time'] = pd.to_datetime(df1['time'], utc=True)

    df2, df3 = pdta.ichimoku(close=close, high=high, low=low, tenkan=N1, kijun=N2, senkou=N3, talib=False)
    df_final = pd.concat([df1, df2], axis=1)

    df_final['signalF'] = 0
    df_final.loc[(df_final['ITS_' + str(N1)] > df_final['IKS_' + str(N2)]) & (close > df_final['IKS_' + str(N2)]), 'signalF'] = 1
    df_final.loc[df_final['ISB_' + str(N2)] > df_final['ISA_' + str(N1)], 'signalF'] = 0

    return df_final


def ICHIMOKU3_timing(df, close, high, low, N1, N2, N3, N4, N5, MA_df, *args, **kwargs):
    df1 = df.copy()
    df1['time'] = pd.to_datetime(df1['time'], utc=True)

    df2, df3 = pdta.ichimoku(close=close, high=high, low=low, tenkan=N1, kijun=N2, senkou=N3, talib=False)
    df_final = pd.concat([df1, df2], axis=1)

    df_final = pd.merge(df_final, MA_df, on='time', how='left')
    df_final['bull'].fillna(method='ffill', inplace=True)

    df_final['signalF'] = 0
    df_final.loc[(df_final['ITS_' + str(N1)] > df_final['IKS_' + str(N2)]) & (close > df_final['IKS_' + str(N2)]) & (df_final['bull'] == 1), 'signalF'] = N4
    df_final.loc[(df_final['ITS_' + str(N1)] > df_final['IKS_' + str(N2)]) & (close > df_final['IKS_' + str(N2)]) & (df_final['bull'] == 0), 'signalF'] = N5
    df_final.loc[df_final['ISB_' + str(N2)] > df_final['ISA_' + str(N1)], 'signalF'] = 0

    return df_final


# --------------------------------------------------------20230608新增，择时，KC
def KC_timing(df, close, high, low, N1, N2, N3, N4, *args, **kwargs):
    df1 = df.copy()
    df1['time'] = pd.to_datetime(df1['time'], utc=True)

    df2 = pdta.kc(close=close, high=high, low=low, length=N1, scalar=N2, talib=False)
    df2.columns = ['KCL', 'KCM', 'KCU']
    df_final = pd.concat([df1, df2], axis=1)

    df_final['signalF'] = 0

    df_final.loc[(close > df_final['KCM']) & (close < df_final['KCU']), 'signalF'] = N3
    df_final.loc[close > df_final['KCU'], 'signalF'] = N4

    return df_final


def KC1_timing(df, close, high, low, N1, N2, N3, N4, N5, N6, MA_df, *args, **kwargs):
    df1 = df.copy()
    df1['time'] = pd.to_datetime(df1['time'], utc=True)

    df2 = pdta.kc(close=close, high=high, low=low, length=N1, scalar=N2, talib=False)
    df2.columns = ['KCL', 'KCM', 'KCU']
    df_final = pd.concat([df1, df2], axis=1)

    df_final = pd.merge(df_final, MA_df, on='time', how='left')
    df_final['bull'].fillna(method='ffill', inplace=True)

    df_final['signalF'] = 0

    df_final.loc[(close > df_final['KCM']) & (close < df_final['KCU']) & (df_final['bull'] == 1), 'signalF'] = N3
    df_final.loc[(close > df_final['KCU']) & (df_final['bull'] == 1), 'signalF'] = N4
    df_final.loc[(close > df_final['KCM']) & (close < df_final['KCU']) & (df_final['bull'] == 0), 'signalF'] = N5
    df_final.loc[(close > df_final['KCU']) & (df_final['bull'] == 0), 'signalF'] = N6

    return df_final


def KC2_timing(df, close, high, low, N1, N2, N3, N4, N5, N6, N7, MA_df, *args, **kwargs):
    df1 = df.copy()
    df1['time'] = pd.to_datetime(df1['time'], utc=True)

    df2 = pdta.kc(close=close, high=high, low=low, length=N1, scalar=N2, talib=False)
    df2.columns = ['KCL', 'KCM', 'KCU']
    df_final = pd.concat([df1, df2], axis=1)

    df_final = pd.merge(df_final, MA_df, on='time', how='left')
    df_final['bull'].fillna(method='ffill', inplace=True)

    df_final['signalF'] = 0

    df_final.loc[(close > df_final['KCM']) & (close < df_final['KCU']) & (df_final['bull'] == 1), 'signalF'] = N3
    df_final.loc[(close > df_final['KCU']) & (df_final['bull'] == 1), 'signalF'] = N4
    df_final.loc[(close > df_final['KCM']) & (close < df_final['KCU']) & (df_final['bull'] == 0), 'signalF'] = N5
    df_final.loc[(close > df_final['KCU']) & (df_final['bull'] == 0), 'signalF'] = N6
    df_final.loc[(close < df_final['KCM']) & (df_final['bull'] == 0), 'signalF'] = N7

    return df_final

# --------------------------------------------------------20230608新增，择时，KC
def SAR_timing(df, close, high, low, *args, **kwargs):
    df1 = df.copy()
    df1['time'] = pd.to_datetime(df1['time'], utc=True)

    df1['SAR'] = talib.SAR(high=high, low=low)

    df1['signalF'] = 0
    df1.loc[close > df1['SAR'], 'signalF'] = 1

    return df1


def SAR1_timing(df, close, high, low, N1, N2, MA_df, *args, **kwargs):
    df1 = df.copy()
    df1['time'] = pd.to_datetime(df1['time'], utc=True)

    df1['SAR'] = talib.SAR(high=high, low=low)

    df1 = pd.merge(df1, MA_df, on='time', how='left')
    df1['bull'].fillna(method='ffill', inplace=True)

    df1['signalF'] = 0
    df1.loc[(close > df1['SAR']) & (df1['bull'] == 1), 'signalF'] = N1
    df1.loc[(close > df1['SAR']) & (df1['bull'] == 0), 'signalF'] = N2

    return df1


# --------------------------------------------------------20230608新增，择时，TD，useless
def TD_timing(df, close, *args, **kwargs):
    df1 = df.copy()
    df1['time'] = pd.to_datetime(df1['time'], utc=True)

    df2 = pdta.td_seq(close=close)
    df2.columns = ['setup', 'countdown']
    df_final = pd.concat([df1, df2], axis=1)

    df_final['signalF'] = np.nan
    df_final.loc[df_final['countdown'] >= 9, 'signalF'] = 1
    df_final.loc[df_final['setup'] >= 7, 'signalF'] = 0
    df_final.fillna(method='ffill', inplace=True)

    df_final.fillna(value=0, inplace=True)

    return df_final


# --------------------------------------------------------20230608新增，择时，CCI
def CCI_timing(df, close, high, low, N1, *args, **kwargs):
    df1 = df.copy()
    df1['time'] = pd.to_datetime(df1['time'], utc=True)

    df1['CCI'] = talib.CCI(close=close, high=high, low=low, timeperiod=N1)

    df1['signalF'] = np.nan
    df1.loc[df1['CCI'] <= -100, 'signalF'] = 0
    df1.loc[df1['CCI'] >= 100, 'signalF'] = 1

    df1.fillna(method='ffill', inplace=True)
    df1.fillna(value=0, inplace=True)

    return df1


def CCI1_timing(df, close, high, low, N1, N2, N3, MA_df, *args, **kwargs):
    df1 = df.copy()
    df1['time'] = pd.to_datetime(df1['time'], utc=True)

    df1['CCI'] = talib.CCI(close=close, high=high, low=low, timeperiod=N1)

    df1 = pd.merge(df1, MA_df, on='time', how='left')
    df1['bull'].fillna(method='ffill', inplace=True)

    df1['signalF'] = np.nan
    df1.loc[df1['CCI'] <= -100, 'signalF'] = 0
    df1.loc[(df1['CCI'] >= 100) & (df1['bull'] == 1), 'signalF'] = N2
    df1.loc[(df1['CCI'] >= 100) & (df1['bull'] == 0), 'signalF'] = N3

    df1.fillna(method='ffill', inplace=True)
    df1.fillna(value=0, inplace=True)

    return df1


# --------------------------------------------------------20240402新增，动量，STOCHk_N1_N2_N3 and STOCHd_N1_N2_N3
def talib_STOCH(df, close, high, low, N1, N2, N3, *args, **kwargs):
    df1 = df.copy()
    df1['STOCHk_' + str(N1) + '_' + str(N2) + '_' + str(N3)], df1['STOCHd_' + str(N1) + '_' + str(N2) + '_' + str(N3)] = talib.STOCH(close=close, high=high, low=low, fastk_period=N1, slowd_period=N2, slowk_period=N3, slowk_matype=0)
    return df1


def pdta_STOCH(df, close, high, low, N1, N2, N3, *args, **kwargs):
    df = df.copy()
    df1 = pdta.stoch(close=close, high=high, low=low, k=N1, d=N2, smooth_k=N3, mamode='sma', talib=False)
    df2 = pd.concat([df, df1], axis=1)
    return df2


# --------------------------------------------------------20240402新增，择时，STOCH
def STOCH_timing(df, close, high, low, N1, N2, N3, N4, N5, *args, **kwargs):
    df1 = df.copy()
    df1['time'] = pd.to_datetime(df1['time'], utc=True)
    df1['k'], df1['d'] = talib.STOCH(close=close, high=high, low=low, fastk_period=N1, slowd_period=N2,
                                     slowk_period=N3, slowk_matype=0)

    df1['signalF'] = 0
    df1.loc[(df1['k'].shift(1) < df1['d'].shift(1)) & (df1['k'] > df1['d']) & (df1['k'] >= N4) & (
            df1['k'] <= N5), 'signalF'] = 1
    df1.loc[(df1['k'] > df1['d']) & (df1['k'] >= N4) & (df1['k'].shift(1) < N4), 'signalF'] = 1
    df1.loc[(df1['k'].shift(1) > df1['d'].shift(1)) & (df1['k'] < df1['d']) & (df1['k'] >= N4) & (
            df1['k'] <= N5), 'signalF'] = -1
    df1.loc[(df1['k'] < df1['d']) & (df1['k'] <= N5) & (df1['k'].shift(1) > N5), 'signalF'] = -1

    return df1


# --------------------------------------------------------20240402新增，量比因子，VRATIO_N1_N2
def talib_VRATIO(df, target, N1, N2, *args, **kwargs):
    df1 = df.copy()
    df1['VRATIO_' + str(N1) + '_' + str(N2)] = talib.SMA(target, timeperiod=N1).astype(float) / talib.SMA(target,
                                                                                                          timeperiod=N2).astype(
        float)
    df1['VRATIO_' + str(N1) + '_' + str(N2)].replace([np.inf, -np.inf], 0, inplace=True)

    return df1


def pdta_VRATIO(df, target, N1, N2, *args, **kwargs):
    df1 = df.copy()
    df1['Vratio_' + str(N1) + '_' + str(N2)] = pdta.sma(target, length=N1, talib=False).astype(float) / pdta.sma(target, length=N2, talib=False).astype(float)
    return df1


# --------------------------------------------------------20240402新增，波动趋势因子，BRATIO_N1_N2
def talib_BRATIO(df, target, N1, N2, *args, **kwargs):
    df1 = df.copy()
    a, b, c = talib.BBANDS(target, timeperiod=N1, nbdevup=2, nbdevdn=2, matype=0)
    a1, b1, c1 = talib.BBANDS(target, timeperiod=N2, nbdevup=2, nbdevdn=2, matype=0)
    df1['BRATIO_' + str(N1) + '_' + str(N2)] = (a.astype(float) - b.astype(float)) / (
                a1.astype(float) - b1.astype(float))
    df1['BRATIO_' + str(N1) + '_' + str(N2)].replace([np.inf, -np.inf], 0, inplace=True)

    return df1


def pdta_BRATIO(df, target, N1, N2, *args, **kwargs):
    df1 = df.copy()

    a = pdta.bbands(target, length=N1, std=2, talib=False)
    b = pdta.bbands(target, length=N2, std=2, talib=False)

    df1['BRATIO_' + str(N1) + '_' + str(N2)] = (a['BBU'].astype(float) - a['BBM'].astype(float)) / (b['BBU'].astype(float) - b['BBM'].astype(float))

    return df1


# --------------------------------------------------------20240402新增，瞬时波动因子，PRATIO_N
def talib_PRATIO(df, target, N, *args, **kwargs):
    df1 = df.copy()
    chg = (target.apply(np.log) - target.shift(1).apply(np.log)).astype(float)
    df1['PRATIO_' + str(N)] = chg / talib.SMA(target, timeperiod=N).astype(float)
    df1['PRATIO_' + str(N)].replace([np.inf, -np.inf], 0, inplace=True)

    return df1


def pdta_PRATIO(df, target, N, *args, **kwargs):
    df1 = df.copy()

    chg = (target.apply(np.log) - target.shift(1).apply(np.log)).astype(float)
    df1['PRATIO_' + str(N)] = chg / pdta.sma(target, length=N, talib=False).astype(float)

    return df1

