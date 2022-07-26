#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 27 15:27:07 2021

@author: ron
"""

import unittest
from Event.event import BarEvent, FillEvent, Direction
from Portfolio.portfolio import Portfolio
from datetime import datetime


class TestPortfolio(unittest.TestCase): 
    def setUp(self):
        self.date_time = datetime(2021, 11, 5, 15, 30, 20)
        self.portfolio = Portfolio(10000)

              
    def test_on_fill_long(self):
        """
        Test long and sell multiple shares of GOOG at various price
        to check the arithmetic and cost handling
        """   
        goog = self.portfolio.fin_instruments
        #buy 5 shares of GOOG
        fillevent = FillEvent(self.date_time, 'GOOG', Direction.LONG, 'NASDAQ', 2000, 5, 1)
        self.portfolio.on_fill(fillevent)
        #sell 2 shares of GOOG
        fillevent = FillEvent(self.date_time, 'GOOG', Direction.SHORT, 'NASDAQ', 3000, 2, 1)
        self.portfolio.on_fill(fillevent)  
        #buy 1 shares of GOOL
        fillevent = FillEvent(self.date_time, 'GOOG', Direction.LONG, 'NASDAQ', 2500, 1, 1)
        self.portfolio.on_fill(fillevent)     
        #sell 3 shares of GOOL
        fillevent = FillEvent(self.date_time, 'GOOG', Direction.SHORT, 'NASDAQ', 3500, 3, 1)
        self.portfolio.on_fill(fillevent)
        
        self.assertEqual(self.portfolio.cash, 14000)
        self.assertEqual(self.portfolio.market_value, 3500)
        self.assertEqual(self.portfolio.get_asset_val(), 17500)
        self.assertEqual(goog.loc['GOOG']['POS'], 1)
        self.assertEqual(goog.loc['GOOG']['AVG_PRICE'], 2125)
        self.assertEqual(goog.loc['GOOG']['MKT_VAL'], 3500)
        self.assertEqual(goog.loc['GOOG']['RLZD_P'], 6125)
        self.assertEqual(goog.loc['GOOG']['UNRLZD_P'], 1375)

         
    def test_on_fill_short(self):
        """
        Test short and buy back multiple shares of GOOG at various price
        to check the arithmetic
        """
        goog = self.portfolio.fin_instruments
        #short 5 shares of GOOG
        fillevent = FillEvent(self.date_time, 'GOOG', Direction.SHORT, 'NASDAQ', 2000, 5, 1)
        self.portfolio.on_fill(fillevent)  
        #buy back 2 shares of GOOG
        fillevent = FillEvent(self.date_time, 'GOOG', Direction.LONG, 'NASDAQ', 1000, 2, 1)
        self.portfolio.on_fill(fillevent) 
        #short 2 shares of GOOL
        fillevent = FillEvent(self.date_time, 'GOOG', Direction.SHORT, 'NASDAQ', 2500, 2, 1)
        self.portfolio.on_fill(fillevent)
        #buy back 3 shares of GOOL
        fillevent = FillEvent(self.date_time, 'GOOG', Direction.LONG, 'NASDAQ', 3500, 3, 1)
        self.portfolio.on_fill(fillevent)
        
        self.assertEqual(self.portfolio.cash, 12500)
        self.assertEqual(self.portfolio.market_value, -7000)
        self.assertEqual(self.portfolio.get_asset_val(), 5500)     
        self.assertEqual(goog.loc['GOOG']['POS'], -2)
        self.assertEqual(goog.loc['GOOG']['AVG_PRICE'], 2200)
        self.assertEqual(goog.loc['GOOG']['MKT_VAL'], -7000)
        self.assertEqual(goog.loc['GOOG']['RLZD_P'], -1900)
        self.assertEqual(goog.loc['GOOG']['UNRLZD_P'], -2600)

        
    def test_on_bar_long(self):
        """
        test if the information updated to a stock is correct
        when the stock is in a long position
        """
        barevent = BarEvent(self.date_time, 'GOOG', 1000, 2500, 900, 2300, 100000)
        fillevent = FillEvent(self.date_time, 'GOOG', Direction.LONG, 'NASDAQ', 2000, 5, 1)
        goog = self.portfolio.fin_instruments
        self.portfolio.on_fill(fillevent)
        self.portfolio.on_bar(barevent)
            
        barevent = BarEvent(self.date_time, 'GOOG', 1000, 2000, 900, 1500, 100000)
        self.portfolio.on_bar(barevent)
        
        self.assertEqual(goog.loc['GOOG']['POS'], 5)
        self.assertEqual(goog.loc['GOOG']['AVG_PRICE'], 2000)
        self.assertEqual(goog.loc['GOOG']['MKT_VAL'], 7500)
        self.assertEqual(goog.loc['GOOG']['RLZD_P'], 0)
        self.assertEqual(goog.loc['GOOG']['UNRLZD_P'], -2500)    
        self.assertEqual(self.portfolio.cash, 0)
        self.assertEqual(self.portfolio.market_value, 7500)
        self.assertEqual(self.portfolio.get_asset_val(), 7500)
     
        
    def test_on_bar_short(self):
        """
        test if the information updated to a stock is correct
        when the stock is in a short position
        """
        barevent = BarEvent(self.date_time, 'GOOG', 1000, 2500, 900, 2300, 100000)
        goog = self.portfolio.fin_instruments
        fillevent = FillEvent(self.date_time, 'GOOG', Direction.SHORT, 'NASDAQ', 2000, 4, 1)
        self.portfolio.on_fill(fillevent)
        self.portfolio.on_bar(barevent)
        
        barevent = BarEvent(self.date_time, 'GOOG', 1000, 2500, 900, 3000, 100000)
        self.portfolio.on_bar(barevent)
        
        self.assertEqual(goog.loc['GOOG']['POS'], -4)
        self.assertEqual(goog.loc['GOOG']['AVG_PRICE'], 2000)
        self.assertEqual(goog.loc['GOOG']['MKT_VAL'], -12000)
        self.assertEqual(goog.loc['GOOG']['RLZD_P'], 0)
        self.assertEqual(goog.loc['GOOG']['UNRLZD_P'], -4000)    
        self.assertEqual(self.portfolio.cash, 18000)
        self.assertEqual(self.portfolio.market_value, -12000)
        self.assertEqual(self.portfolio.get_asset_val(), 6000)
               

        
if __name__ == '__main__':
    unittest.main(verbosity=2)
        

                

        