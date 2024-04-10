#!/usr/bin/env python3
from sklearn.preprocessing import MinMaxScaler, StandardScaler
import joblib
import numpy as np
from pkg_resources import resource_filename
import fire, warnings
from dataclasses import dataclass
#import asyncio
#from multiprocessing import Pool

@dataclass
class Regbot:
  opening: float
  high: float
  asks: float
  bids: float
  vc: float
  ema_26: float
  ema_12: float
  macd: float
  macdsignal: float
  macd_histogram: float
  low: float
  grad_histogram: float
  mean_grad_hist: int
  close: float
  pct_change: float
  volume: float
  grad_vol_sma: float
  ratio4: float
  rsi_05: float
  rsi_15: float
  sma_25: float
  close_grad: float
  close_grad_neg: float
  grad_sma_25: float
  long_kdj: int
  long_grad_kdj: float
  long_jcrosk: int
  short_kdj: int
  short_grad_kdj: float


  reg_model_path: str = resource_filename(__name__, 'minute_model.pkl')
  scaler_path: str = resource_filename(__name__, 'minutescaler.gz')

  def loadmodel(self):
    try:
      return joblib.load(open(f'{self.reg_model_path}', 'rb'))
    except Exception as e:
      print(e)


  def prepareInput(self):
    stuff = [self.opening, self.high, self.asks, self.bids, self.vc, self.ema_26,
                            self.ema_12, self.macd, self.macdsignal, self.macd_histogram, self.low,
                            self.grad_histogram, self.mean_grad_hist, self.close, self.pct_change,
                            self.volume, self.grad_vol_sma, self.ratio4, self.rsi_05, self.rsi_15,
                            self.sma_25, self.close_grad, self.close_grad_neg, self.grad_sma_25,
                            self.long_kdj, self.long_grad_kdj, self.long_jcrosk, self.short_kdj,
                            self.short_grad_kdj]
    try:
      test_data = np.array([stuff]
                            )
      scaler = joblib.load(f'{self.scaler_path}')
      return scaler.transform(test_data)
    except Exception as e:
      print(e)


  def buySignalGenerator(self):
    try:
      model = self.loadmodel()
      data = self.prepareInput().reshape(1,-1)
      return (model.predict(data)).astype(int)[0]
    except Exception as e:
      print(e)


def signal(*args):
    try:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")
            return Regbot(*args).buySignalGenerator()
    except Exception as e:
        print(e)
'''
def signal(*args):
    try:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")
            with Pool(processes=1) as pool:
                # Use apply_async instead of apply
                result = pool.apply_async(Regbot(*args).buySignalGenerator)
                prediction = result.get()  # Retrieve the result
                return prediction # prediction[0] -> enter_long, prediction[1] -> enter_short and prediction[2] -> do_nothing
    except Exception as e:
        return {'Error': e}
'''



if __name__ == '__main__':
  fire.Fire(signal)
