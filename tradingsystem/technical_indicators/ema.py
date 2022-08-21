#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 20 14:35:19 2021

@author: ron
"""

from .base import AbstractTechnicalIndicator


class EMA(AbstractTechnicalIndicator):
    
    def __init__(self, period):
        self.period = period
        self.prev_ema = 0
        self.lastest_val = 0
        self.data_store = []
        self.ready = False
        self.multiplier = 2 / (period + 1)
        self.first_ema_count = 0


    def update(self, price):
        #data needed for the first EMA
        if self.first_ema_count < self.period:
            self.prev_ema += price
            self.first_ema_count += 1
            if self.first_ema_count == self.period:
                self.ready = True
            
        if self.ready:   
            if self.first_ema_count == self.period:
                self.lastest_val = self.prev_ema / self.period
                self.first_ema_count += 1
            else:
                self.lastest_val = (price - self.prev_ema) * self.multiplier + self.prev_ema
                
            self.prev_ema = self.lastest_val
            self.data_store.append(self.lastest_val)

                          
    def __bool__(self):
        return self.ready
            
            
                   
                    
            
                
                
                    
            
            
            
        