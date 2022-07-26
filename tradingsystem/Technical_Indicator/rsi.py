#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 16 20:16:45 2021

@author: ron
"""

from Technical_Indicator.base import AbstractTechnicalIndicator


class RSI(AbstractTechnicalIndicator):
    
    def __init__(self, period):
        self.period = period
        self.prev_close = None
        self.lastest_val = 0
        self.data_store = []
        self.avg_gain = 0
        self.avg_loss = 0
        self.ready = False
        self.first_rsi_count = 0        


    def update(self, price):
        if self.prev_close is not None:
            gain, loss = self._gain_loss(price)
            #need data for calculating first rsi...
            if self.first_rsi_count < self.period:
                self.avg_gain += gain            
                self.avg_loss += loss
                    
                self.first_rsi_count += 1
                if not self.ready and self.first_rsi_count == self.period:  
                    self.ready = True
                    
            
            #data is engough for calculating rsi...
            if self.ready:
                #averge gain and loss for the first rsi
                if self.first_rsi_count == self.period:
                    self.avg_gain = self.avg_gain / self.period
                    self.avg_loss = self.avg_loss / self.period
                    self.first_rsi_count += 1
                #average gain and loss for subsequent rsi    
                else:
                    self.avg_gain = (self.avg_gain * (self.period - 1) + gain) / self.period
                    self.avg_loss = (self.avg_loss * (self.period - 1) + loss) / self.period   
                    
                try:            
                    rsi = 100 - (100 / (1 + (self.avg_gain / self.avg_loss)))                    
                #no loss
                except ZeroDivisionError:
                    rsi = 100
                
                self.lastest_val = rsi
                self.data_store.append(rsi)
        self.prev_close = price
                                                     

    def _gain_loss(self, price):
        cur_gain_loss = price - self.prev_close
        if cur_gain_loss > 0:
            return cur_gain_loss, 0
        else:
            return 0, abs(cur_gain_loss)
        
                
    def __bool__(self):
        return self.ready
                    
            
                
                
                    
            
            
            
        