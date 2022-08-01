#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec  7 20:05:06 2021

@author: ron
"""


from IBTWS.ibapi.wrapper import EWrapper
import datetime
from Event.event import Direction
from copy import deepcopy
from common import Bar, Error
from IBTWS.ibapi.common import TickerId, TickAttrib
from decimal import Decimal
from ibapi.ticktype import * # @UnusedWildImport
import time


class TWSWrapper(EWrapper):
    
    def __init__(self):
        EWrapper.__init__(self)


    def historicalData(self, reqId, bar):
        """ returns the requested historical data bars
        reqId - the request's identifier
        date  - the bar's date and time (either as a yyyymmss hh:mm:ssformatted
             string or as system time according to the request)
        open  - the bar's open point
        high  - the bar's high point
        low   - the bar's low point
        close - the bar's closing point
        volume - the bar's traded volume if available
        count - the number of trades during the bar's timespan (only available
            for TRADES).
        WAP -   the bar's Weighted Average Price
        hasGaps  -indicates if the data has gaps or not. """
        #--------------------------------------------------       
        bar.date += " GMT+0000"
        timestamp = int(datetime.datetime.strptime(bar.date, "%Y%m%d  %H:%M:%S GMT%z").timestamp()) #bar start time
 
        if timestamp >= self.last_bar_time:
            current_bar = Bar(timestamp, timestamp + 5, bar.open, bar.high,
                             bar.low, bar.close, bar.volume, bar.wap, bar.barCount)
            self._construct_bar(reqId, current_bar)

      
    def historicalDataEnd(self, reqId, start, end): 
        """ Marks the ending of the historical bars reception. """
        print('Start Date: {start_date}, End Date: {end_date}'.format(start_date=start, end_date=end))              
        with self.cond:
            self.cond.notify_all()

        
    def realtimeBar(self, reqId, time, open_, high, low, close, volume, wap, count):
        current_bar = Bar(time, time + 5, open_, high,
                          low, close, volume, wap, count)      

        if current_bar.end_time >= self.last_bar_time:
            self._construct_bar(reqId, current_bar) 

        if not self.realtime_subscribed:
            with self.cond:
                self.realtime_subscribed = True
                self.cond.notify_all()       


    def historicalDataUpdate(self, reqId, bar):
        #print("In historicalDataUpdate")
        """returns updates in real time when keepUpToDate is set to True"""
        bar.date += " GMT+0000"
        timestamp = int(datetime.datetime.strptime(bar.date, "%Y%m%d  %H:%M:%S GMT%z").timestamp())
        bar.date = timestamp
        print(reqId, bar)           
        current_bar = Bar(timestamp, timestamp + 5, bar.open, bar.high,
                           bar.low, bar.close, bar.volume, bar.wap, bar.barCount)


    def nextValidId(self, orderId):
        with self.cond:
            self.nextValidOrderId = orderId
            self.cond.notify_all()


    def openOrder(self, orderId, contract, order, orderState):
        super().openOrder(orderId, contract, order, orderState)
        #print("-------------------------------")
        # print("OpenOrder. PermId: ", order.permId, "ClientId:", order.clientId, " OrderId:", orderId, 
        #         "Account:", order.account, "Symbol:", contract.symbol, "SecType:", contract.secType,
        #         "Exchange:", contract.exchange, "Action:", order.action, "OrderType:", order.orderType,
        #         "TotalQty:", decimalMaxString(order.totalQuantity), "CashQty:", order.cashQty, 
        #         "LmtPrice:", order.lmtPrice, "AuxPrice:", order.auxPrice, "Status:", orderState.status) 

        
    def orderStatus(self, orderId, status, filled,
                    remaining, avgFillPrice, permId,
                    parentId, lastFillPrice, clientId,
                    whyHeld, mktCapPrice):
        super().orderStatus(orderId, status, filled,
                    remaining, avgFillPrice, permId,
                    parentId, lastFillPrice, clientId,
                    whyHeld, mktCapPrice)
        #print("-------------------------------")
        # print("OrderStatus. Id:", orderId, "Status:", status, "Filled:", decimalMaxString(filled),
        #         "Remaining:", decimalMaxString(remaining), "AvgFillPrice:", avgFillPrice,
        #         "PermId:", permId, "ParentId:", parentId, "LastFillPrice:",
        #         lastFillPrice, "ClientId:", clientId, "WhyHeld:",
        #         whyHeld, "MktCapPrice:", mktCapPrice)

        
    def execDetails(self, reqId, contract, execution):
        execution.time += " GMT+0000"
        timestamp = int(datetime.datetime.strptime(execution.time , "%Y%m%d  %H:%M:%S GMT%z").timestamp())        
        self.fill_event.timestamp = timestamp
        
        if contract.secType == "STK":       
            self.fill_event.ticker = contract.symbol
        elif contract.secType == "CASH":       
            self.fill_event.ticker = contract.symbol + "/" + contract.currency
            
        if execution.side == "BOT":
            self.fill_event.direction = Direction.LONG
        else:
            self.fill_event.direction = Direction.SHORT
            
        self.fill_event.exchange = execution.exchange
        self.fill_event.price = execution.price
        self.fill_event.quantity = int(execution.shares)

            
    def commissionReport(self, commissionReport):
        self.fill_event.commission = commissionReport.commission
        self.execution_detail.put(deepcopy(self.fill_event))
        #print("CommissionReport.", commissionReport)
        
 
    def completedOrder(self, contract, order, orderState):
        print("------------------------------------------")
        print("Contract:", contract)
        print("order:", order)
        """This function is called to feed in completed orders.

        contract: Contract - The Contract class attributes describe the contract.
        order: Order - The Order class gives the details of the completed order.
        orderState: OrderState - The orderState class includes completed order status details."""
   
    
    def headTimestamp(self, reqId:int, headTimestamp:str):
        """returns earliest available data of a type of data for a particular contract"""
        print(headTimestamp)
        
        
    def error(self, reqId, errorCode, errorString):
        """This event is called when there is an error with the
        communication or when TWS wants to send a message to the client."""
        super().error(reqId, errorCode, errorString)
        time_now  = time.time()
        error = Error(time_now, errorCode, errorString)
        self.error_code.put(errorCode)


    def currentTime(self, time: int):
        with self.cond:
            self.time = time
            self.cond.notify_all()
        # print("tws time:", time)


    def tickPrice(self, reqId:TickerId , tickType:TickType, price:float,
                  attrib:TickAttrib):
        """Market data tick price callback. Handles all price related ticks."""
        super().tickPrice(reqId, tickType, price, attrib)
        print("TickPrice. TickerId:", reqId, "tickType:", tickType,
            "Price:", str(price), "CanAutoExecute:", attrib.canAutoExecute,
            "PastLimit:", attrib.pastLimit, end=' ')
        if tickType == TickTypeEnum.BID or tickType == TickTypeEnum.ASK:
            print("PreOpen:", attrib.preOpen)
        else:
            print() 


    def tickSize(self, reqId:TickerId, tickType:TickType, size:Decimal):
        """Market data tick size callback. Handles all size-related ticks."""
        super().tickSize(reqId, tickType, size)
        #print("TickSize. TickerId:", reqId, "TickType:", tickType, "Size: ", str(size))


    def tickSnapshotEnd(self, reqId:int):
        """When requesting market data snapshots, this market will indicate the
        snapshot reception is finished. """
        super().tickSnapshotEnd(reqId)


    def tickGeneric(self, reqId: TickerId, tickType: TickType, value: float):
        super().tickGeneric(reqId, tickType, value)
        print("TickGeneric. TickerId:", reqId, "TickType:", tickType, "Value:", str(value))
