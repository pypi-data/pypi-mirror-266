# Evx regpredict mlbot

This is a simplified version of [evxpredictor](https://pypi.org/project/evxpredictor/) package used to generate buy and sell signals for crypto and conventional stock markets based on the excess volume indicator(EVX). EVX is a concept where the bid-ask spread is estimated inherently from current market prices. 

You can read more about Evx in the whitepaper [here](https://www.researchgate.net/publication/345313655_DeFiPaper)  
# Installation
Install regpredict with `python3 -m pip install regpredict`  
# Usage

In your python script simply import the module and use as follows:

```  
from regpredict.regbot import signal
print(signal(20,65,85,78,45,0.7))
```
The above methods take an assets a,b,macd,macdsignal,grad_histogram,close_gradient,close_gradient_neg based on the time interval you have chosen. A zero classification output would instruct the user to sell, while one output means don't sell or buy if the asset is not already present in the orders.  

# Testing an entire dataframe
Testing of a dataframe for correct buy, sell signals is as simple as applying the function as follows:  

```
import pandas as pd
from regbot import signal
#from regpredict.regbot import signal
df = pd.read_csv('../path/to/your_validation.csv')

y_pred = []
def getSignal(a,b,macd,macdsignal,grad_histogram,close_gradient,close_gradient_neg):
    return signal(a,b,macd,macdsignal,grad_histogram,close_gradient,close_gradient_neg)

Where thr is a user defined threshold.


df = df[df['enter_long'] == 1]
print(df.head())

df['result'] = df.apply(lambda row: getSignal(row['a'],row['b'],row['macd'],row['macdsignal'],row['grad-histogram'],row['close-gradient']row['close-gradient-neg']), axis=1)

print(df.head())

print(len(df[df['result'] == df['enter_long']]), len(df))

```

Your original data must already have some presumed 'buy' signal.

# Warning
This is not financial advise. Regpredict is entirely on its preliminary stages. Use it at your own risk.
