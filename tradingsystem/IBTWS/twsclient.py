#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec  7 20:02:36 2021

@author: ron
"""

from IBTWS.twswrapper import TWSWrapper
from IBTWS.ibapi.client import EClient
from IBTWS.contracts import Contracts
from Event.event import BarEvent, FillEvent
import threading
from time import sleep
import queue
from copy import deepcopy


"""
The main thread will exit whenever it is finished 
executing all the code in your script 
that is not started in a separate thread.
"""
class TWSClient(TWSWrapper, EClient):

    exchange = "SMART"
    
    def __init__(self):
        """
        timeframe: trading timeframe, use in real time trading   
        """
        TWSWrapper.__init__(self)
        EClient.__init__(self, wrapper=self)
        #for thread-safe
        self.fill_event =  FillEvent(None, None, None, None, None, None, None)
        #for storing the fill_event, then ib_broker will get the FIllEvent in the queue  
        self.execution_detail = queue.Queue()
        self.nextValidOrderId = 0
        #store the error code raised by the api, the main program
        #will get it and perform subseqent actions
        self.error_code = queue.Queue()
        self.host = None
        self.port = None
        self.clientId = None


    def connect(self, host, port, clientId=0):    
        print("Connecting to tws...")
        super().connect(host, port, clientId)
        
    
    def run(self):
        if self.isConnected():
            print("Running tws client...")            
            #create thread for running the EClient message loop
            t1 = threading.Thread(target=super().run, name="EClient.run Thread")                                  
            t1.start()   
            sleep(1)
        
        else:
            print("TWS client is not connected to tws yet!")
            
            
    def reqHistoricalData(self, reqId , contract, endDateTime,
                          durationStr, barSizeSetting, whatToShow="TRADES",
                          useRTH=1, formatDate=1, keepUpToDate=False):
        super().reqHistoricalData(reqId, contract, endDateTime,
                                 durationStr, barSizeSetting, whatToShow,
                                 useRTH, formatDate, keepUpToDate, [])  
        #time.sleep(1)


    def reqRealTimeBars(self, ticker_list, timeframe, whatToShow, useRTH):
        #reqRealTimeBars returns bar in every 5 seconds
        #these 5 second bars are then constructed into bar with defined timeframe by calling _construct_bar()
        #then it puts it into latest_bar_event queue which Data Handler can get the latest Bar Event                
        self.ticker_list = ticker_list
        self.timeframe = timeframe
        self._bars = {k: BarEvent(None, ticker_list[k], None, -1, 999999, None, 0 ) for k in range(0, len(ticker_list))}
        self.lastest_bar_event = queue.Queue()
        self.contracts_list = []
        self.whatToShow = whatToShow
        self.useRTH = useRTH
        #ib return starting time of the bar
        self.last_bar_time = 0 
        self.realtime_subscribed = False
        for ticker in ticker_list:
            #base, quote = ticker.split(".")
            #self.contracts_list.append(Contracts.FX(base, quote))
            self.contracts_list.append(Contracts.USStock(ticker))

        # for ticker in ticker_list:
        #     base, quote = ticker.split(".")
        #     self.contracts_list.append(Contracts.FX(base, quote))           

        self.time = 0
        self.reqCurrentTime()
        sleep(0.1)
        next_divisable = self.time + (timeframe - self.time % timeframe)
        sleep(next_divisable - self.time + 5)  
                                                    
        for i in range(0, len(self.contracts_list)):
            super().reqRealTimeBars(i, self.contracts_list[i], 5, self.whatToShow, self.useRTH, [])


    def resubscribe_RealTimeBars(self):
        """
        Since reqRealTimeBars may stop working 
        after IB server reset or between trading sessions
        it is necessary to resubscribe the real time bars       
        """
        #cancel exisiting subscription and resubscribe again
        #self.realtime_subscribed = False
        for i in range(0, len(self.contracts_list)):
            print("cancelling real time bars...")
            super().reqRealTimeBars(i, self.contracts_list[i], 5, self.whatToShow, self.useRTH, [])        

    
    def reqHeadTimeStamp(self, reqId, contract, whatToShow, useRTH, formatDate):
        """returns earliest available data of a type of data for a particular contract"""
        super().reqHeadTimeStamp(reqId, contract, whatToShow, useRTH, formatDate)
            

    def _construct_bar(self, ticker_id, current_bar):
        #constrtuct bar from 5 seconds bar in defined timeframe
        bar = self._bars[ticker_id]
        if bar.open_price == None and bar.timestamp == None:
            bar.open_price = current_bar.open_price
            bar.timestamp = current_bar.start_time
            # print("start time:", bar.timestamp)

        bar.high_price = max(bar.high_price, current_bar.high_price)
        bar.low_price = min(bar.low_price, current_bar.low_price)
        
        if current_bar.end_time != self.last_bar_time:           
            bar.volume += current_bar.volume
            
        #5 seconds bars are enough to create a bar with defined timeframe
        if (current_bar.end_time - bar.timestamp) >= self.timeframe:
            # if(current_bar.end_time - bar.timestamp) > self.timeframe:
            #     print("there are 5sec bars missing in this bar")                
            bar.close_price = current_bar.close_price        
            self.lastest_bar_event.put(deepcopy(bar))
            #init next bar            
            bar.timestamp = None            
            bar.open_price = None
            bar.high_price = -1
            bar.low_price = 999999
            bar.close_price = None
            bar.volume = 0   
                                 
        self.last_bar_time = current_bar.end_time
            

     