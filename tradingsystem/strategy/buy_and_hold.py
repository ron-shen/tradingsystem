#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 13 19:51:56 2021
@author: ron
"""

from .base import AbstractStrategy
from ..event.event import SignalEvent, OrderType, Direction
from ..common import get_cur_time

class BuyAndHold(AbstractStrategy):
    """
    session_type: 'backtest' or 'live'
    """
    
    def __init__(self, event_queue, session_type, long_only=True, 
                 stoploss=None, portfolio_handler=None, db_client=None
        ):
        
        self.db_client = db_client
        self.tickers_data = {}
        self.event_queue = event_queue
        self.invested = False
        self.long_only = long_only
        self.session_type = session_type
        
        if stoploss is not None and portfolio_handler is None:
            raise ValueError("portfolio_handler must be set in order to calculate stop loss")
        else:
            self.stoploss = stoploss
            self.portfolio_handler = portfolio_handler

    
    def calculate_signal(self, bar_event):           
            if not self.invested:                    
                cur_time = get_cur_time(bar_event, self.session_type)
                signal_event = SignalEvent(cur_time, bar_event.ticker,
                                           OrderType.MARKET, Direction.LONG, 
                                           bar_event.close_price)
                print(signal_event)
                self.event_queue.put(signal_event)
                self.invested = True
                
                
    def get_ticker(self):
        return self.tickers_data

    
    def __str__(self):
        return "Buy And Hold Strategy"