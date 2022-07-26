#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 29 18:22:08 2021

@author: ron
"""
import queue
from Event.event import EventType
from Data_Handler.historical_bar_handler import HistoricalBarHandler, get_data_from_yahoo_finance, get_data_from_csv
from Strategy.sma_crossover import SMACrossover
from Strategy.bb import BollingerBands
from Strategy.rsi import RelativeStrengthIndex
from Strategy.macd import MACDCrossover
from Strategy.ema_crossover import EMACrossover
from Strategy.macdrsi import MACDRSI
from Portfolio.portfolio import Portfolio
from Order_Handler.max_order_handler import MaxOrderHandler
from Broker_Handler.simulated_broker import IBSimulatedBroker
from Statistics.statistics import Statistics
from common import SessionType



class TradingSession:
    """
    Enscapsulates the settings and components for
    carrying out either a backtest or live trading session.
    """
    def __init__(
        self, price_handler, strategy, portfolio, 
        order_handler, broker, events_queue,
        statistics
        ):
        """
        Set up the backtest variables according to
        what has been passed in.
        """
        self.strategy = strategy
        self.events_queue = events_queue
        self.data_handler = price_handler
        self.portfolio = portfolio
        self.order_handler = order_handler
        self.broker = broker
        self.statistics = statistics
        self.previous_day = None


    def run_session(self):
        """
        Carries out an infinite while loop that polls the
        events queue and directs each event to either the
        strategy component of the execution handler. The
        loop continue until the event queue has been
        emptied.
        """
        while True:
            try:
                event = self.events_queue.get(False)
            except queue.Empty:
                try:
                    self.data_handler.get_next()
                except StopIteration:
                    #get the update of last day and break out the while loop
                    self.statistics.update(self.previous_day, self.portfolio.get_asset_val())                                  
                    break
            else:
                if self.previous_day is None:
                    self.previous_day = event.timestamp.date()
                elif event.timestamp.date() > self.previous_day:
                    self.statistics.update(self.previous_day, self.portfolio.get_asset_val())
                    self.previous_day = event.timestamp.date()  

                if event.type == EventType.BAR:
                    self.strategy.calculate_signal(event)
                    self.portfolio.on_bar(event)                  
                elif event.type == EventType.SIGNAL:
                    self.order_handler.create_order(event)
                elif event.type == EventType.ORDER:
                    self.broker.execute_order(event)
                elif event.type == EventType.FILL:
                    self.portfolio.on_fill(event)
                else:
                    raise NotImplementedError("Unsupported event.type '%s'" % event.type)


    def start_trading(self, testing=False):
        """
        Runs either a backtest or live session, and outputs performance when complete.
        """
        self.run_session()
        print("---------------------------------")
        print('Ending cash: ' + str(self.portfolio.cash))
        print('Ending market value: ' + str(self.portfolio.market_value))
        print('Ending asset value: ' + str(self.portfolio.get_asset_val()))
        results = self.statistics.get_results()
        print("---------------------------------")
        print("Strategy:", self.strategy)
        print("Return: %0.2f%%" % results["return"])
        print("Sharpe Ratio: %0.2f" % results["sharpe_ratio"])
        print(
            "Max Drawdown: %0.2f%%" % (
                results["max_drawdown"] * 100.0
            )
        )
        return_over_mdd = results["return"] / (results["max_drawdown"] * 100 * -1)
        print("Return Over Maximum Drawdown: %0.2f" % return_over_mdd)
        print("Backtest complete.")
        self.statistics.plot_results()
 
            
#set up     
events_queue = queue.Queue()       

init_asset_val = 10000

tickers_data = {}
amzn5m = get_data_from_csv('./Data/AMZN.csv')
ticker_list = ['AMZN']
tickers_data['AMZN'] = amzn5m
historical_bar_handler = HistoricalBarHandler(tickers_data, events_queue)


portfolio = Portfolio(init_asset_val)
order_handler = MaxOrderHandler(portfolio, events_queue, SessionType.BACKTEST)

sma_crossover = SMACrossover(ticker_list, 10, 20, events_queue, SessionType.BACKTEST, portfolio)
ema_crossover = EMACrossover(ticker_list, 10, 20, events_queue, SessionType.BACKTEST, portfolio)
bb = BollingerBands(ticker_list, 20, 2, events_queue, SessionType.BACKTEST, portfolio)
rsi = RelativeStrengthIndex(ticker_list, 14, events_queue, SessionType.BACKTEST, portfolio)
macd = MACDCrossover(ticker_list, 12, 26, 9, events_queue, SessionType.BACKTEST, portfolio)
macdrsi = MACDRSI(ticker_list, 12, 26, 9, 14, events_queue, SessionType.BACKTEST, portfolio)

simulated_broker = IBSimulatedBroker(events_queue, historical_bar_handler)

stat = Statistics(init_asset_val)

trading_session = TradingSession(historical_bar_handler, macdrsi, portfolio, 
                                 order_handler ,simulated_broker, events_queue, stat)


#start backtest
trading_session.start_trading()



