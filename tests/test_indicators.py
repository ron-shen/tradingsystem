#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 22 20:12:56 2021

@author: ron
"""

import unittest
from tradingsystem.technical_indicators.sma import SMA
from tradingsystem.technical_indicators.bb import BB
from tradingsystem.technical_indicators.rsi import RSI
from tradingsystem.technical_indicators.ema import EMA
from tradingsystem.technical_indicators.macd import MACD
import talib as ta
import math
import yfinance as yf

class TestIndicators(unittest.TestCase):
    #test indicators and compare the result with talib 
    def setUp(self):
        self.historical_bar_data = yf.download('TSLA', start='2021-01-01', end='2021-11-01')['Close']

      
    def test_sma(self):
        sma = SMA(20)
        tasma = ta.SMA(self.historical_bar_data, 20)
        tasma = [round(val,3) for val in tasma if not math.isnan(val)]
        for val in self.historical_bar_data:
            sma.update(val)
        sma_round = [round(val,3) for val in sma.data_store]
        self.assertListEqual(sma_round, tasma)

        
    def test_bb(self):
        bb = BB(20, 2)
        tabb = ta.BBANDS(self.historical_bar_data, timeperiod=20)
        tabb = [[round(val,3) for val in band if not math.isnan(val)] for band in tabb]
        for val in self.historical_bar_data:
            bb.update(val)            
        bb_round = [[round(val,3) for val in band] for band in bb.data_store]
        self.assertListEqual(bb_round, tabb)

        
    def test_rsi(self):
        rsi = RSI(20)
        tarsi = ta.RSI(self.historical_bar_data, 20)
        tarsi = [round(val,3) for val in tarsi if not math.isnan(val)]
        for val in self.historical_bar_data:
            rsi.update(val)
        rsi_round = [round(val,3) for val in rsi.data_store]
        self.assertListEqual(rsi_round, tarsi)    
        
    
    def test_ema(self):
        ema = EMA(14)
        taema = ta.EMA(self.historical_bar_data, 14)
        taema = [round(val,3) for val in taema if not math.isnan(val)]
        for val in self.historical_bar_data:
            ema.update(val)
        ema_round = [round(val,3) for val in ema.data_store]
        self.assertListEqual(ema_round, taema) 


    def test_macd(self):
        """
        Not test with talib since the MACD formula in talib is different
        """
        self.data = [459.99, 448.85, 446.06, 450.81, 442.8, 448.97, 444.57, 441.4,
                     430.47, 420.05, 431.14, 425.66, 430.58, 431.72, 437.87, 428.43,
                     428.35, 432.5, 443.66, 455.72, 454.49, 452.08, 452.73, 461.91, 
                     463.58, 461.14, 452.08, 442.66, 428.91, 429.79, 431.99, 427.72,
                     423.2, 426.21, 426.98, 435.69]     
        
        macd = MACD(12,26,9)
        expected_result = [[-2.071, -2.622, -2.329], [3.038, 1.906, 1.059], [-5.108, -4.527, -3.388]]
        for val in self.data:
            macd.update(val)
        macd_round = [[round(val,3) for val in r] for r in macd.data_store]
        self.assertListEqual(macd_round, expected_result)             
        
        

if __name__ == '__main__':
    unittest.main(verbosity=2)