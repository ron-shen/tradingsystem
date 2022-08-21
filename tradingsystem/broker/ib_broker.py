#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 17 12:46:25 2021

@author: ron
"""
from .base import AbstractBroker
from ..event.event import Direction
from ..ibtws.orders import Orders
from ..ibtws.contracts import create_contract
import queue
import time


class IBBroker(AbstractBroker):
    
    def __init__(self, twsclient, event_queue, ticker_list, db_client=None):
        self.db_client = db_client
        self.event_queue = event_queue
        self.twsclient = twsclient
        self.contracts_list = {}
        for ticker in ticker_list:
            self.contracts_list[ticker] = create_contract(ticker)
  
     
    def execute_order(self, order_event):
        if time.time() - order_event.timestamp >= 300:
            print("Order rejected as the signal generated is at least 5 mins before")
        
        else:
            self.twsclient.reqIds()
            if order_event.direction == Direction.LONG:
                order = Orders.MarketOrder("BUY", order_event.quantity)

            #order_event.direction == Direction.SHORT    
            else:
                order = Orders.MarketOrder("SELL", order_event.quantity)
                
            self.twsclient.placeOrder(self.twsclient.nextValidOrderId, self.contracts_list[order_event.ticker], order)


    def get_fill_event(self):
        try:
            fill_event = self.twsclient.execution_detail.get(False)
        except queue.Empty:
            pass
        else:
            print(fill_event)
            self.event_queue.put(fill_event)
            if self.db_client is not None:
                self.save_to_db(fill_event)        
       
