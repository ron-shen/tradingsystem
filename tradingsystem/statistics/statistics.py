import pandas as pd
import numpy as np
from math import sqrt
import matplotlib.pyplot as plt


class Statistics:
    """
    Simple Statistics provides a bare-bones example of statistics
    that can be collected through trading.
    Statistics included are Sharpe Ratio, Drawdown, Max Drawdown,
    Max Drawdown Duration.
    TODO need some kind of trading-frequency parameter in setup.
    Sharpe calculations need to know if daily, hourly, minutely, etc.
    """
    def __init__(self, init_asset_value):
        self.init_asset_value = init_asset_value
        self.drawdowns = []
        self.timeseries = []
        # Initialize in order for first-step calculations to be correct.
        self.hwm = [init_asset_value]
        self.asset_value = []
        #self.bars = []
        self.returns = []


    def update(self, timestamp, asset_value):
        """
        Update all statistics that must be tracked over time.
        """
        self.timeseries.append(timestamp)
        self.asset_value.append(asset_value)
        # Calculate Drawdown.
        self.hwm.append(max(self.hwm[-1], self.asset_value[-1]))
        self.drawdowns.append((self.asset_value[-1] - self.hwm[-1])/self.hwm[-1])
        
        if len(self.asset_value) > 1:
            pct = ((self.asset_value[-1] - self.asset_value[-2]) / self.asset_value[-2])
            self.returns.append(pct)


    def get_results(self):
        """
        Return a dict with all important results & stats.
        """
        statistics = {}
        statistics["return"] = ((self.asset_value[-1] - self.init_asset_value) 
                               / self.init_asset_value) * 100
        statistics["sharpe_ratio"] = self.calculate_sharpe_ratio(0.01)
        statistics["max_drawdown"] = min(self.drawdowns)

        return statistics


    def calculate_sharpe_ratio(self, benchmark_return=0.00, N=252):
        """
        Calculate the sharpe ratio of our portfolio.
        Expects benchmark_return to be, for example, 0.01 for 1%
        """
        return_series = pd.Series(self.returns)
        return_annual = return_series.mean() * N
        sd_return_annual = return_series.std(ddof=1) * sqrt(N)
        return (return_annual - benchmark_return) / sd_return_annual


    def annualised_sharpe(self, returns, N=252):
        """
        Calculate the annualised Sharpe ratio of a returns stream
        based on a number of trading periods, N. N defaults to 252,
        which then assumes a stream of daily returns.
        The function assumes that the returns are the excess of
        those compared to a benchmark.
        """
        return np.sqrt(N) * returns.mean() / returns.std()


    def calculate_max_drawdown_pct(self):
        """
        Calculate the percentage drop related to the "worst"
        drawdown seen.
        """
        drawdown_series = pd.Series(self.drawdowns)
        equity_series = pd.Series(self.equity)
        bottom_index = drawdown_series.idxmax()
        try:
            top_index = equity_series[:bottom_index].idxmax()
            pct = (
                (equity_series.ix[top_index] - equity_series.ix[bottom_index]) /
                equity_series.ix[top_index] * 100
            )
            return round(pct, 4)
        except ValueError:
            return np.nan


    def plot_results(self):
        """
        A simple script to plot the balance of the portfolio, or
        "equity curve", as a function of time.
        """
        fig, axs = plt.subplots(2)
        axs[0].title.set_text('Equity Curve')
        axs[1].title.set_text('Drawdowns vs Time')
        axs[0].set(xlabel="Time",ylabel="Portfolio Value ($)")
        axs[1].set(xlabel="Time",ylabel="Drawdowns (%)")

        axs[0].plot(self.timeseries, self.asset_value)
        drawdownper = [ele*100 for ele in self.drawdowns]
        axs[1].plot(self.timeseries, drawdownper)
        plt.show()               

