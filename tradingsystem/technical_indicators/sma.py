#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 13 19:32:15 2021

@author: ron
"""

from .base import AbstractTechnicalIndicator
from collections import deque
import numpy as np

class SMA(AbstractTechnicalIndicator):
    
    def __init__(self, period):
        """
        Parameters
        ----------
        ready: to indicate whether data is sufficent to calucalte the result 
        """        
        self.data = deque(maxlen=period)
        self.data_store = []
        self.lastest_val = 0
        self.period = period
        self.ready = False

    def update(self, price):
        self.data.append(price)      
        #data is sufficient
        if not self.ready and len(self.data) == self.period:
            self.ready = True
            
        if self.ready:
            self.lastest_val = np.mean(self.data)
            self.data_store.append(self.lastest_val)

    
    def __bool__(self):
        return self.ready