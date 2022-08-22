#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 13 18:43:54 2021

@author: ron
"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone


class AbstractStrategy(ABC):
    """
    AbstractStrategy is an abstract base class 
    for all strategy class
    ------------------
    """
    @abstractmethod
    def calculate_signal(self, bar_event):
        pass
    
    
    def save_to_db_signal(self, signal_event):
        query = ("INSERT INTO SignalEvent (Datetime, Ticker, Order_Type, Direction, Closing_Price, Entry_Price)"
                "VALUES (%s, %s, %s, %s, %s, %s)"
        )
        timestamp_converted = datetime.fromtimestamp(signal_event.timestamp, timezone.utc)
        data = (timestamp_converted, signal_event.ticker, signal_event.order_type.name, signal_event.direction.name, 
                signal_event.bar_closing_price, signal_event.entry_price)
        cursor = self.db_client.cursor()
        cursor.execute(query, data)
        self.db_client.commit()  
    
    


