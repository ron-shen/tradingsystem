#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 29 18:22:08 2021

@author: ron
"""
import queue
from .event.event import EventType


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
 




