#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 20 15:16:52 2021

@author: ron
"""

from .base import AbstractTechnicalIndicator
from .ema import EMA


class MACD(AbstractTechnicalIndicator):
    
    def __init__(self, short_period, long_period, signal_period):
        """
        Parameters
        ----------
        data_store : list of lists
                     First list stores macd value
                     Second list stores macd signal value
                     Third list stores macd histogram value
        """        
        self.ema_short = EMA(short_period)
        self.ema_long = EMA(long_period)
        self.ema_signal = EMA(signal_period)
        self.lastest_val = []
        self.data_store = [[],[],[]]
        self.ready = False
        
        
    def update(self, price):
        self.ema_short.update(price)
        self.ema_long.update(price)
        if self.ema_short and self.ema_long:
            #macd line
            macd = self.ema_short.lastest_val - self.ema_long.lastest_val
            self.ema_signal.update(macd)
            if not self.ready and self.ema_signal:
                self.ready = True
                
            if self.ready:
                macd_signal = self.ema_signal.lastest_val
                macd_histogram = macd - macd_signal
                self.lastest_val = [macd, macd_signal, macd_histogram]
                self.data_store[0].append(macd)
                self.data_store[1].append(macd_signal)
                self.data_store[2].append(macd_histogram)
                               
                        
    def __bool__(self):
        return self.ready
                
                
                
            
            
        
        

            
            
                   
                    
            
                
                
                    
            
            
            
        