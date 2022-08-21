#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 14 11:36:51 2021

@author: ron
"""
from .base import AbstractTechnicalIndicator
from .sma import SMA
import numpy as np


class BBData:
    def __init_(self):
        self.upper = 0
        self.mid = 0
        self.lower = 0


class BB(AbstractTechnicalIndicator):
    
    def __init__(self, period, multiple):  
        """
        Parameters
        ----------
        data_store : list of lists
                   First list stores upperbound value
                   Second list stores mid value
                   Third list stores lowerbound value
        """
        self.sma = SMA(period)
        self.data_store = [[], [], []]
        self.lastest_val = BBData()
        self.k = multiple
        self.ready = False


    def update(self, price):
        #calculate lastest sma
        self.sma.update(price)
        if not self.ready and self.sma:
            self.ready = True
              
            
        if self.ready:
            mid = self.sma.lastest_val
            sd = np.std(self.sma.data)
            upper = mid + self.k * sd
            lower = mid - self.k * sd
            self.lastest_val.upper = upper
            self.lastest_val.mid = mid
            self.lastest_val.lower = lower
            self.data_store[0].append(upper)
            self.data_store[1].append(mid)
            self.data_store[2].append(lower)


    def __bool__(self):
        return self.ready

    
    