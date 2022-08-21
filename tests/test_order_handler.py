#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 28 12:51:56 2021

@author: ron
"""
import unittest
from tradingsystem.order_handler.fixed_order_handler import FixedOrderHandler
from tradingsystem.order_handler.max_order_handler import MaxOrderHandler
from tradingsystem.event.event import SignalEvent, OrderType, Direction
from tradingsystem.portfolio.portfolio import Portfolio
from datetime import datetime
from tradingsystem.common import SessionType
import queue


class TestPositionHandler(unittest.TestCase):   
    def setUp(self):        
        self.portfolio = Portfolio(10000)
        self.date_time = datetime(2021, 11, 5, 15, 30, 20)
        self.event_queue = queue.Queue()

      
    def test_fixed_position(self):
        fixed = FixedOrderHandler(5, self.portfolio, self.event_queue, SessionType.BACKTEST)
        #test buy
        signal = SignalEvent(self.date_time, 'GOOG', OrderType.MARKET, Direction.LONG, 2821.990)
        fixed.create_order(signal)
        order_event = self.event_queue.get()
        self.assertEqual(order_event.quantity, 5)
        #test sell
        signal = SignalEvent(self.date_time, 'GOOG', OrderType.MARKET, Direction.SHORT, 2821.990)
        fixed.create_order(signal)
        order_event = self.event_queue.get()
        self.assertEqual(order_event.quantity, 5)
        
        
    def test_max_position(self):
        max_order = MaxOrderHandler(self.portfolio, self.event_queue, SessionType.BACKTEST)
        #test buy
        signal = SignalEvent(self.date_time, 'GOOG', OrderType.MARKET, Direction.LONG, 2821.990)
        max_order.create_order(signal)
        order_event = self.event_queue.get()
        self.assertEqual(order_event.quantity, 3)
        #test sell
        signal = SignalEvent(self.date_time, 'GOOG', OrderType.MARKET, Direction.SHORT, 1230)
        max_order.create_order(signal)
        order_event = self.event_queue.get()
        self.assertEqual(order_event.quantity, 8)

    
    def test_max_position_not_enough_cash(self):
        max_order = MaxOrderHandler(self.portfolio, self.event_queue, SessionType.BACKTEST)
        #test buy
        signal = SignalEvent(self.date_time, 'GOOG', OrderType.MARKET, Direction.LONG, 50000)
        max_order.create_order(signal)
        self.assertEqual(self.event_queue.qsize(), 0)





if __name__ == '__main__':
    unittest.main(verbosity=2)     
        
        