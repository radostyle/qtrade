import numpy as np
import pandas as pd
import ta
import matplotlib.pyplot as plt
import yfinance as yf
import quantstats as qs
import webbrowser

class Strategy():
    def __init__(self, security_name, start, end):
        self.security_name = security_name
        self.start = start
        self.end = end

    def download_data(self):
        security = yf.Ticker(self.security_name)
        data = security.history(interval='1d', start=self.start, end=self.end)
        return data
    def get_psar(self, data):
        myindicator = ta.trend.PSARIndicator(data.High, data.Low, data.Close)
        psar_series = myindicator.psar()
        return psar_series
    def get_signals(self, data, indicator):
        signal = np.where(data.Close > indicator, 1, np.where(data.Close < indicator, -1, 0))
        return signal
    def get_equity_curve(self, data):
        data['Daily Returns'] = data['Close'].pct_change() * data['Signal'].shift(1)
        # data['Cumulative Returns'] = (1.0 * data['Daily Returns']).cumprod() * 100.0
        data['Cumulative Returns'] = (1.0 + data['Daily Returns']).cumprod()
        data['Benchmark'] = data['Close'] / data['Close'].iloc[0] * 100.
        return data

    def get_equity_curve2(self, data):
        data['Daily Returns'] = data['Close'].pct_change() * data['Signal']
        # data['Cumulative Returns'] = (1.0 * data['Daily Returns']).cumprod() * 100.0
        data['Cumulative Returns'] = (1.0 + data['Daily Returns']).cumprod()
        data['Benchmark'] = data['Close'] / data['Close'].iloc[0] * 100.
        return data

def plot_psar():
    security_name = 'SSO'
    start_date = '2015-01-01'
    end_date = '2023-01-01'

    mystrategy = Strategy(security_name, start_date, end_date)
    print(mystrategy.security_name, mystrategy.start, mystrategy.end)

    result = mystrategy.download_data()
    mypsar = mystrategy.get_psar(result)

    print(result)
    print("\n\n", mypsar)


    plt.plot(mypsar.index, mypsar.values, label='PSAR',linestyle='--' )
    plt.plot(result.index, result.Close, label='Close')
# Find crossover points
    cross_above = (mypsar > result.Close) & (mypsar.shift(1) <= result.Close.shift(1))
    cross_below = (mypsar < result.Close) & (mypsar.shift(1) >= result.Close.shift(1))
# Plot green arrows for upward crossovers
    plt.scatter(result.index[cross_above], result.Close[cross_above], marker='^', color='green', label='Buy Signal')
    plt.scatter(result.index[cross_below], result.Close[cross_below], marker='v', color='red', label='Sell Signal')
    plt.grid(True)
    plt.legend()
    plt.show()



    signal = mystrategy.get_signals(result,  mypsar)
    result["Signal"] = signal

    result = mystrategy.get_equity_curve(result)
    plt.plot(result['Cumulative Returns'])
# plt.plot(result['Signal'])
    plt.show()

class OtherStrategy():
    def __init__(self, security_name, start, end):
        self.security_name = security_name
        self.start = start
        self.end = end

    def download_data(self):
        security = yf.Ticker(self.security_name)
        data = security.history(interval='1d', start=self.start, end=self.end)
        return data
    def calculate_trading_days(self, result):
        result["constant"] =1
        result["trading_day_of_year"]=result.groupby(pd.Grouper(freq='Y'))[['constant']].cumsum()
    def my_strategy_signal(self, result):
        self.pick_dates = ((result["trading_day_of_year"] >= 50) & (result["trading_day_of_year"] <= 84)) | ((result["trading_day_of_year"] >= 93) & (result["trading_day_of_year"] <= 153)) | ((result["trading_day_of_year"] >= 188) & (result["trading_day_of_year"] <= 251))

        signal = np.where(self.pick_dates== True, 1, 0)
        return signal

    def run(self):
        self.result = self.download_data()
        self.calculate_trading_days(self.result)
        equity_curve = self.calculate(self.result)
        self.result = equity_curve

        plt.plot(equity_curve['Cumulative Returns'])
        return equity_curve
    def calculate(self, result):
        my_strategy_signal = self.my_strategy_signal(result)
        result['Signal'] = my_strategy_signal
        equity_curve = self.get_equity_curve2(result)
        return equity_curve
    def get_signals(self, data, indicator):
        signal = np.where(data.Close > indicator, 1, np.where(data.Close < indicator, -1, 0))
        return signal
    def get_equity_curve(self, data):
        data['Daily Returns'] = data['Close'].pct_change() * data['Signal'].shift(1)
        # data['Cumulative Returns'] = (1.0 * data['Daily Returns']).cumprod() * 100.0
        data['Cumulative Returns'] = (1.0 + data['Daily Returns']).cumprod()
        data['Benchmark'] = data['Close'] / data['Close'].iloc[0] * 100.
        return data

    def get_equity_curve2(self, data):
        data['Daily Returns'] = data['Close'].pct_change() * data['Signal']
        # data['Cumulative Returns'] = (1.0 * data['Daily Returns']).cumprod() * 100.0
        data['Cumulative Returns'] = (1.0 + data['Daily Returns']).cumprod()
        data['Benchmark'] = data['Close'] / data['Close'].iloc[0] * 100.
        return data

class TurnOfMonthStrategy():
    def __init__(self, security_name, start, end):
        self.security_name = security_name
        self.start = start
        self.end = end

    def download_data(self):
        security = yf.Ticker(self.security_name)
        data = security.history(interval='1d', start=self.start, end=self.end)
        return data
    def calculate_trading_days(self, result):
        result["trading_days_in_month"] = result.groupby(pd.Grouper(freq='M')).transform("size")
        result["trading_days_in_month"]
        result["constant"] =1
        result["trading_day_of_month"] = result.groupby(pd.Grouper(freq='M'))[["constant"]].transform("cumsum")
        result["trading_days_til_month_end"] = result["trading_days_in_month"] - result["trading_day_of_month"]
        result["trading_days_til_month_end"]
    def my_strategy_signal(self, result):
        import numpy as np
        signal = np.where(result['trading_days_til_month_end'] <= 4, 1, np.where(result['trading_day_of_month'] <= 2, 1, 0))
        return signal

    def run(self):
        self.result = self.download_data()
        self.calculate_trading_days(self.result)
        equity_curve = self.calculate(self.result)

        plt.plot(equity_curve['Cumulative Returns'])
        return equity_curve
    def calculate(self, result):
        my_strategy_signal = self.my_strategy_signal(result)
        result['Signal'] = my_strategy_signal
        equity_curve = self.get_equity_curve2(result)
        return equity_curve
    def get_signals(self, data, indicator):
        signal = np.where(data.Close > indicator, 1, np.where(data.Close < indicator, -1, 0))
        return signal
    def get_equity_curve(self, data):
        data['Daily Returns'] = data['Close'].pct_change() * data['Signal'].shift(1)
        # data['Cumulative Returns'] = (1.0 * data['Daily Returns']).cumprod() * 100.0
        data['Cumulative Returns'] = (1.0 + data['Daily Returns']).cumprod()
        data['Benchmark'] = data['Close'] / data['Close'].iloc[0] * 100.
        return data

    def get_equity_curve2(self, data):
        data['Daily Returns'] = data['Close'].pct_change() * data['Signal']
        # data['Cumulative Returns'] = (1.0 * data['Daily Returns']).cumprod() * 100.0
        data['Cumulative Returns'] = (1.0 + data['Daily Returns']).cumprod()
        data['Benchmark'] = data['Close'] / data['Close'].iloc[0] * 100.
        return data
#https://medium.com/analytics-vidhya/a-simple-day-and-night-strategy-using-python-a36c18578161
# need to know days that are 5 business days before end
# 01=1,02=2,04=3
# 30-p[0], 30-p[1] days left
#
# 468 *.015
# 7.020
# 468 + 7
# 475

# 60% of the time you make 72%
# 40% of the time you lose everything
# I sell and I make 60% of the time.
# 6.85
# 40% of the time I have to buy back the stock and sell it and I lose a little bit - how much?

# 1691 - 1610
# 81/ 1610
# .05031055900621118012 * 100
# 5
# 5.00 * .05
# .2500
# 5.25




