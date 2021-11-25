import pandas as pd

from typing import Tuple


def simple_moving_average(df: pd.DataFrame, n: int = 10, prices: str = 'Close') -> pd.Series:
  """
  Calculate simple n-day moving average for given data.
  """
  return df[prices].rolling(window=n, min_periods=n).mean()


def weighted_moving_average(df: pd.DataFrame, n: int = 10, prices: str = 'Close') -> pd.Series:
  """
  Calculate weighted n-day moving average for given data.
  """
  return df[prices].rolling(window=n, min_periods=n).apply(lambda x: x[::-1].cumsum().sum() * 2 / n / (n + 1))


def exponential_moving_average(df: pd.DataFrame, n: int = 10, prices: str = 'Close') -> pd.Series:
    """
    Calculate exponential n-day moving average for given data.
    """
    return df[prices].ewm(span=n, min_periods=n).mean()
  
  
def relative_strength_index(df: pd.DataFrame, n: int, prices: str = 'Close') -> pd.Series:
  """
  Calculate n-day relative strength index for given data.
  """
  deltas = df[prices].diff()
  ups = deltas.clip(lower=0)
  downs = (-deltas).clip(lower=0)
  rs = ups.ewm(com=n-1, min_periods=n).mean() / downs.ewm(com=n-1, min_periods=n).mean()
  rsi = 100 - 100 / (1 + rs)
  return rsi


def stochastic_oscillator(df: pd.DataFrame, n_k: int = 14, n_d: int = 3,
                          prices: str = 'Close', d_type: str = 'sma') -> pd.Series:
  """
  Calculate n-day stochastic %K and %D for given data.
  """
  highest_high = df[prices].rolling(window=n_k, min_periods=n_k).max()
  lowest_low = df[prices].rolling(window=n_k, min_periods=n_k).min()

  stochastic_k = pd.DataFrame(((df[prices] - lowest_low) / (highest_high - lowest_low)) * 100)

  if d_type == 'sma': 
      stochastic_d = simple_moving_average(stochastic_k, n_d)
  elif d_type == 'wma':
      stochastic_d = weighted_moving_average(stochastic_k, n_d)
  elif d_type == 'ema':
      stochastic_d = exponential_moving_average(stochastic_k, n_d)
  else:
      raise ValueError('Only SMA, WMA and EMA are available.')

  return stochastic_k, stochastic_d


def bollinger_bands(df: pd.DataFrame, n: int = 20, m: float = 2.0) -> Tuple[pd.Series]:
  """
  Calculate bollinger bands for given data.
  """
  typical_price = (df['High'] + df['Low'] + df['Close']) / 3

  sma = typical_price.rolling(window=n, min_periods=n).mean()
  sigma = typical_price.rolling(window=n, min_periods=n).std()

  upper_bollinger_band = sma + m * sigma
  lower_bollinger_band = sma - m * sigma

  return lower_bollinger_band, upper_bollinger_band


def moving_average_convergence_divergence(df: pd.DataFrame, n_fast: int = 12, 
                                          n_slow: int = 26, n_signal: int = 9) -> Tuple[pd.Series]:
    """
    Calculate MACD, MACD Signal and MACD difference for given data.
    """
    ema_fast = exponential_moving_average(df, n=n_fast)
    ema_slow = exponential_moving_average(df, n=n_slow)

    macd = ema_fast - ema_slow
    macd_signal = macd.ewm(span=n_signal, min_periods=n_signal).mean()
    macd_difference = macd - macd_signal

    return macd, macd_signal, macd_difference
