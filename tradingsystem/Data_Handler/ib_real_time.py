#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 14 14:43:25 2021

@author: ron
"""
from Data_Handler.base import AbstractDataHandler
import queue
import time
from common import check_ping



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
                 whatToShow, useRTH, event_queue, 
                 db_client=None
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
        self.twsclient.reqRealTimeBars(self.ticker_list, self.timeframe, 
                                       self.whatToShow, self.useRTH)
        print("Wait until first real time bar return...")
        while not self.twsclient.realtime_subscribed:
            pass
        print("Data Subscription is successful!")                               


    def check_bar_interruption(self):
        #check if bars arrive in expected time
        #if data is not arrived within 600s, resubscribe again                    
            current_time = time.time()                 
            if current_time - self.twsclient.last_bar_time >= 600:
                ping_success_count = 0
                print("Data isn't arrived in expected time, backfill missing data and resubscribe...")                               
                #ensure network is connected
                #only 5 successive ping success will forward
                print("testing network connection...")
                while ping_success_count < 5:
                    if (check_ping()):
                        ping_success_count += 1
                    else:
                        ping_success_count = 0
                print("network is ok!")
                print("check if it is connected to IB...")
                if not self.twsclient.isConnected():
                    print("tws is not connected, reconnect again...")
                    self.twsclient.connect("127.0.0.1", 7497, clientId=0)
                    time.sleep(1)
                    if self.twsclient.isConnected():
                        print("reconnection is successful!")
                        self.twsclient.run()
                else:
                    print("tws is connected!")
                    print("cancelling existing subscribtion...")
                    for i in range(0, len(self.twsclient.contracts_list)):
                        self.twsclient.cancelRealTimeBars(i)
                self.twsclient.realtime_subscribed = False                    
                time.sleep(30)
                print("backfill missing data....")
                self.resubscribe()
                while not self.twsclient.realtime_subscribed:
                    pass               


    def resubscribe(self):
        """
        after a historical data farm is disconnected,
        wait IB to connect it again.
        backfill the bars missing during the disconnected period,
        then request real time bar again
        """
        self.twsclient.reqCurrentTime()
        time.sleep(0.1)
        end_time = self.twsclient.time - (self.twsclient.time % 5)
        time_missing = end_time - self.twsclient.last_bar_time
        if time_missing < 60:
            duration_str = "60 S"
        else:
            duration_str = str(time_missing) + " S"
            
        for i in range(0, len(self.twsclient.contracts_list)):                
            self.twsclient.reqHistoricalData(i, self.twsclient.contracts_list[i], "",
                                                duration_str, "5 secs", whatToShow="MIDPOINT", 
                                                keepUpToDate=False)
      