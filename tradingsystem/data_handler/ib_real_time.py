#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 14 14:43:25 2021

@author: ron
"""
from .base import AbstractDataHandler
import queue
import time
from ..common import check_ping



class IBRealTimeBarHandler(AbstractDataHandler):
    """
    Get real time bar data using tws api
    Parameters
    ----------
    twsclient : an instance of TWSClient
    timeframe: trading timeframe, it needs to be multiple of 5
    You may refer to https://interactivebrokers.github.io/tws-api/historical_bars.html
    for valid input of whatToShow and useRTH
    """
    def __init__(self, twsclient, ticker_list, timeframe, 
                 whatToShow, useRTH, event_queue, db_client=None
        ):
        self.db_client = db_client
        self.twsclient = twsclient
        self.event_queue = event_queue
        self.ticker_list = ticker_list
        self.timeframe = timeframe
        self.whatToShow = whatToShow
        self.useRTH = useRTH
        self.bars_store = []
        self.twsclient.realtime_config(self.ticker_list, self.timeframe, 
                                       self.whatToShow, self.useRTH)

                
    def get_next(self):
        try:
            bar_event = self.twsclient.lastest_bar_event.get(False)
        except queue.Empty:
            pass
        else:
            #convert to readable time
            #print("putting bar event")
            print(bar_event)
            self.event_queue.put(bar_event)
            self.bars_store.append(bar_event)
            if self.db_client is not None:
                self.save_to_db(bar_event)

                                   
    def request_data(self):
        #call this function first before calling get_next()
        self.twsclient.reqRealTimeBars()
        # while not self.twsclient.realtime_subscribed:
        #     pass
                                     
   
    def cancel_subscription(self):
        if self.twsclient.realtime_subscribed:
            self.twsclient.cancel_subscription()
        
        
    def check_bar_interruption(self):
        #check if bars arrive in expected time
        #if data is not arrived within 5mins, resubscribe again                    
            current_time = time.time()                 
            if current_time - self.twsclient.last_bar_time >= 300:
                print("Data isn't arrived in expected time, backfill missing data and resubscribe...")                               
                #ensure network is connected
                print("testing network connection...")
                if check_ping():
                    print("network is ok!")
                else:
                    raise Exception("network is not connected...")
                
                print("check if it is connected to IB...")
                if not self.twsclient.isConnected():
                    print("tws is not connected, reconnect again...")
                    self.twsclient.connect()
                    print("reconnection is successful!")
                    self.twsclient.run()

                print("tws is connected...")
                self.cancel_subscription()
                                    
                print("backfill missing data....")
                self.resubscribe()
                self.request_data()             


    def resubscribe(self):
        """
        after a historical data farm is disconnected,
        wait IB to connect it again.
        backfill the bars missing during the disconnected period,
        then request real time bar again
        """
        self.twsclient.reqCurrentTime()
        end_time = self.twsclient.time - (self.twsclient.time % 5)
        time_missing = end_time - self.twsclient.last_bar_time
        if time_missing < 60:
            duration_str = "60 S"
        else:
            duration_str = str(time_missing) + " S"
            
        self.twsclient.reqHistoricalData(duration_str)

            

      