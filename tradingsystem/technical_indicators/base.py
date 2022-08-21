#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 13 19:29:40 2021

@author: ron
"""
from abc import ABC, abstractmethod


class AbstractTechnicalIndicator(ABC):
    """
    AbstractTechnicalIndicator is an abstract base class 
    for all technical indicator class
    """
    @abstractmethod
    def update(self, price):
        pass
    
    
    