#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 22 20:12:56 2021

@author: ron
"""

import unittest
from Event.event import BarEvent, SignalEvent, OrderEvent, FillEvent, OrderType, EventType, Direction
from datetime import datetime


class TestIndicators(unittest.TestCase):
    
    def setUp(self):
        self.date_time = datetime(2021, 11, 5, 15, 30, 20)

              
    def test_BarEvent(self):
         bar = BarEvent(self.date_time, 'GOOG', 2779.970, 2843.540, 2774.959, 2821.990, 105448)
         self.assertEqual(bar.type, EventType.BAR)
         self.assertEqual(bar.timestamp, self.date_time)
         self.assertEqual(bar.ticker, 'GOOG')
         self.assertEqual(bar.open_price, 2779.970)
         self.assertEqual(bar.high_price, 2843.540)
         self.assertEqual(bar.low_price, 2774.959)
         self.assertEqual(bar.close_price, 2821.990)
         self.assertEqual(bar.volume, 105448)
        

                
    def test_SignalEvent_Market(self):
         signal = SignalEvent(self.date_time, 'GOOG', OrderType.MARKET, Direction.LONG, 2821.990)
         self.assertEqual(signal.type, EventType.SIGNAL)
         self.assertEqual(signal.timestamp, self.date_time)
         self.assertEqual(signal.ticker, 'GOOG')
         self.assertEqual(signal.order_type, OrderType.MARKET)
         self.assertEqual(signal.direction, Direction.LONG)
         self.assertEqual(signal.bar_closing_price, 2821.990)
         self.assertEqual(signal.entry_price, None)
         
         
    def test_SignalEvent_Limit(self):
         signal = SignalEvent(self.date_time, 'GOOG', OrderType.LIMIT, Direction.LONG, 2821.990, 2820)
         self.assertEqual(signal.type, EventType.SIGNAL)
         self.assertEqual(signal.timestamp, self.date_time)
         self.assertEqual(signal.ticker, 'GOOG')
         self.assertEqual(signal.order_type, OrderType.LIMIT)
         self.assertEqual(signal.direction, Direction.LONG)
         self.assertEqual(signal.bar_closing_price, 2821.990)
         self.assertEqual(signal.entry_price, 2820)

        
    
    def test_OrderEvent(self):
         order = OrderEvent(self.date_time, 'GOOG', OrderType.MARKET, Direction.LONG, 100)
         self.assertEqual(order.type, EventType.ORDER)
         self.assertEqual(order.timestamp, self.date_time)
         self.assertEqual(order.ticker, 'GOOG')
         self.assertEqual(order.order_type, OrderType.MARKET)
         self.assertEqual(order.direction, Direction.LONG)
         self.assertEqual(order.quantity, 100)



    def test_FillEvent(self):   
         fill = FillEvent(self.date_time, 'GOOG', Direction.LONG, 'NASDAQ', 2821.990, 100, 1)
         self.assertEqual(fill.type, EventType.FILL)
         self.assertEqual(fill.timestamp, self.date_time)
         self.assertEqual(fill.ticker, 'GOOG')
         self.assertEqual(fill.exchange, 'NASDAQ')
         self.assertEqual(fill.price, 2821.990)
         self.assertEqual(fill.quantity, 100)
         self.assertEqual(fill.commission, 1)
        
        

if __name__ == '__main__':
    unittest.main(verbosity=2)

