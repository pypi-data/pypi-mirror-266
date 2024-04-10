import pandas as pd
from mlevx import signal # when running the files
#from regpredict.regbot import signal as signal # when installed as pip library
df = pd.read_csv('../reinforce/regbot_v68_validation.csv')
print(df.columns)

def getSignal(*args):

    #args = [opening, high, asks, bids, vc, ema_26, ema_12, macd, macdsignal, macd_histogram, \
    #        low, grad_histogram, mean_grad_hist, close, pct_change, volume, grad_vol_sma, ratio4, \
    #        rsi_05, rsi_15, sma_25, close_grad, close_grad_neg, grad_sma_25, long_kdj,long_grad_kdj, \
    #        long_jcrosk, short_kdj, short_grad_kdj
    #        ]
    try:
        return signal(*args)
    except Exception as e:
        print(e)

print(df.columns)
#print(df.columns)
df = df.sample(frac=1).reset_index(drop=True)
#print(df.head())
cols = ['enter_long_test', 'enter_short_test', 'do_nothing_test']

df = df[df['targets'] == -1].tail(200)
#print(df.head())

df['result'] = df.apply(lambda row: getSignal(  row['open'], row['high'], row['a'], row['b'], row['vc'], row['ema-26'], row['ema-12'], row['macd'],
                                                row['macdsignal'], row['macd-histogram'], row['low'], row['grad-histogram'],
                                                row['mean-grad-hist'], row['close'], row['pct-change'], row['volume'], row['grad-vol-sma'],
                                                row['ratio4'], row['rsi-05'], row['rsi-15'], row['sma-25'], row['close-gradient'],
                                                row['close-gradient-neg'], row['grad-sma-25'], row['long_kdj'], row['long_grad_kdj'],
                                                row['long_jcrosk'], row['short_kdj'], row['short_grad_kdj']
                                              ), axis=1)

print(df.head())

print(len(df[df['result'] == df['targets']]), len(df))
