#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 17 20:41:09 2021

@author: ron
"""

from Strategy.base import AbstractStrategy
from Technical_Indicator.bb import BB
from Technical_Indicator.rsi import RSI
from Event.event import SignalEvent, OrderType, Direction
from common import get_cur_time



class BBRSI(AbstractStrategy):
    
    def __init__(self, bb_period, multiple, rsi_period,
                 event_queue, session_type, 
                 long_only=True, stoploss=None, 
                 portfolio_handler=None,
                 db_client=None
        ):
        """
        Parameters
        ----------
        tickers_data : dict: {key:string, value: list}
                       key is the ticker symbol, e.g. 'GOOG'
                       list[0] stores BB object.
                       list[1] stores RSI object.
                       
        session_type: 'backtest' or 'live'
        -------

        """
        self.db_client = db_client
        self.bb_period = bb_period
        self.multiple = multiple
        self.rsi_period = rsi_period
        self.tickers_data = {}
        self.event_queue = event_queue
        self.invested = False
        self.session_type = session_type
        
        if stoploss is not None and portfolio_handler is None:
            raise Exception("portfolio_handler must be set in order to calculate stop loss")
        else:
            self.stoploss = stoploss
            self.portfolio_handler = portfolio_handler

    
    def calculate_signal(self, bar_event):
        if not bar_event.ticker in self.tickers_data:
            self._subscribe_ticker(bar_event.ticker)
            
        self.tickers_data[bar_event.ticker][0].update(bar_event.close_price)
        self.tickers_data[bar_event.ticker][1].update(bar_event.close_price)
        
        if self.tickers_data[bar_event.ticker][0] and \
           self.tickers_data[bar_event.ticker][1]:
                             
            upper, mid, lower = self.tickers_data[bar_event.ticker][0].get_lastest_val()
            rsi = self.tickers_data[bar_event.ticker][1].get_lastest_val()
            
            if bar_event.close_price <= lower and rsi <= 30 and not self.invested:
                cur_time = get_cur_time(bar_event, self.session_type)
                signal_event = SignalEvent(cur_time, bar_event.ticker,
                                           OrderType.MARKET, Direction.LONG, 
                                           bar_event.close_price)
                                  
                self.event_queue.put(signal_event)
                self.invested = True
                print(signal_event)
                
            elif ((bar_event.close_price >= upper and rsi >= 70) or self._stop_loss_trigger(bar_event)) \
                 and self.invested:
                cur_time = get_cur_time(bar_event, self.session_type)
                signal_event = SignalEvent(cur_time, bar_event.ticker,
                                           OrderType.MARKET, Direction.EXIT, 
                                           bar_event.close_price)
                                    
                self.event_queue.put(signal_event)
                self.invested = False    
                print(signal_event)
             
    
    def _stop_loss_trigger(self, bar_event):
        if self.stoploss is None:
            return False
        else:
            avg_price = self.portfolio_handler.get_fin_instrucements(bar_event.ticker)["AVG_PRICE"]
            loss = (avg_price - bar_event.close_price) / avg_price
            if loss > self.stoploss:
                return True
            else:
                return False

            
    def _subscribe_ticker(self, ticker_name):
            bb = BB(self.bb_period, self.multiple)
            rsi = RSI(self.rsi_period)
            data = [bb, rsi]
            self.tickers_data[ticker_name] = data
            a = self.tickers_data[ticker_name]

        
    def __str__(self):
        return "BB-RSI Strategy"