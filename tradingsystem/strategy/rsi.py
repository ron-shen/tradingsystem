#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 13 19:51:56 2021

@author: ron
"""

from .base import AbstractStrategy
from ..event.event import SignalEvent, OrderType, Direction
from ..technical_indicators.rsi import RSI
from ..common import get_cur_time


class RelativeStrengthIndex(AbstractStrategy):
    def __init__(self, ticker_list, period, 
                 event_queue, session_type, portfolio,
                 db_client=None
        ):
        """
        Parameters
        ----------
        ticker_list: The ticker symbols used for this strategy
        session_type: SessionType.LIVE or SessionType.BACKTEST
        ---------
        """
        """
        tickers_data: dict: {key:string, value: list}
                key is the ticker symbol, e.g. 'GOOG'
                list[0] stores short sma object.
                list[1] stores long sma object.
        """
        self.db_client = db_client
        self.period = period
        self.tickers_data = self._subscribe_ticker(ticker_list)
        self.event_queue = event_queue
        self.session_type = session_type
        self.portfolio = portfolio


    def calculate_signal(self, bar_event):        
        ticker_data = self.tickers_data[bar_event.ticker]  
        ticker_data.update(bar_event.close_price)
        
        if ticker_data:              
            rsi = ticker_data.lastest_val
            ticker_info = self.portfolio.get_fin_instrument(bar_event.ticker)
            #the ticker symbol has not been long/short yet
            if ticker_info is None:
                #go long
                if rsi <= 30:                    
                    cur_time = get_cur_time(bar_event, self.session_type)
                    signal_event = SignalEvent(cur_time, bar_event.ticker,
                                               OrderType.MARKET, Direction.LONG, 
                                               bar_event.close_price)
                    print(signal_event)
                    self.event_queue.put(signal_event)

                #go short   
                elif rsi >= 70:
                    cur_time = get_cur_time(bar_event, self.session_type)
                    signal_event = SignalEvent(cur_time, bar_event.ticker,
                                               OrderType.MARKET, Direction.SHORT, 
                                               bar_event.close_price)
                    print(signal_event)
                    self.event_queue.put(signal_event)

            #the ticker symbol has been long/short                                       
            else:
                #close long position 
                if ticker_info.POS > 0 and rsi >= 70:
                    cur_time = get_cur_time(bar_event, self.session_type)
                    signal_event = SignalEvent(cur_time, bar_event.ticker,
                                               OrderType.MARKET, Direction.SHORT, 
                                               bar_event.close_price)                                       
                    self.event_queue.put(signal_event)
                    print(signal_event)
                            
                #close short position            
                elif ticker_info.POS < 0 and rsi <= 30:                              
                    cur_time = get_cur_time(bar_event, self.session_type)
                    signal_event = SignalEvent(cur_time, bar_event.ticker,
                                            OrderType.MARKET, Direction.LONG, 
                                            bar_event.close_price)                
                    self.event_queue.put(signal_event)
                    print(signal_event)              

                        
    def _subscribe_ticker(self, ticker_list):
        tickers_data = {}
        for ticker in ticker_list:
            tickers_data[ticker] = RSI(self.period) 
        return tickers_data                                                                                        

            
    def get_ticker_data(self, ticker):
        if not ticker in self.tickers_data:
            return None

        return self.tickers_data[ticker]

    
    def __str__(self):
        return "RSI"
    
        
            
