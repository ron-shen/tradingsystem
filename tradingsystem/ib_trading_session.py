#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 18 19:32:03 2021

@author: ron
"""

import queue
from Event.event import EventType
from Data_Handler.ib_real_time import IBRealTimeBarHandler
from Strategy.sma_crossover import SMACrossover
from Order_Handler.max_order_handler import MaxOrderHandler
from Portfolio.portfolio import Portfolio
from Broker_Handler.ib_broker import IBBroker
from Statistics.statistics import Statistics
from IBTWS.twsclient import TWSClient
from Strategy.macdrsi import MACDRSI
from time import sleep
from datetime import datetime, timezone, time, date, timedelta
from common import SessionType, check_ping
from mysql.connector import connect, Error





class TradingSession:
    """
    Enscapsulates the settings and components for
    carrying out a live trading session through Interactive Brokers.
    """    
    def __init__(
        self, twsclient, price_handler, 
        strategy, portfolio, 
        order_handler, broker, events_queue,
        mkt_open, mkt_close, trading_end, statistics=None, 
        ):
        """
        TODO
        1. now we have to set market open and close time manually, 
           it is better to generate the time automatically
        2. Now if there are public holidays in weekday, the program will
           still run, it shoud make a trading schedule which has a list of the
           publich holidays and trading hours each day 
        3. Now it only supports UTC time, it should support other time zones

        """
        self.strategy = strategy
        self.events_queue = events_queue
        self.price_handler = price_handler
        self.portfolio = portfolio
        self.order_handler = order_handler
        self.broker = broker
        self.statistics = statistics
        self.twsclient = twsclient
        self.previous_day = None
        self.mkt_open = mkt_open
        #give some time to get the last bar
        self.mkt_close = time(mkt_close.hour, 1)
        self.trading_end = trading_end + timedelta(minutes=1)

             
    def run_session(self):
        """
        Carries out an infinite while loop that polls the
        events queue and directs each event to either the
        strategy component of the execution handler. The
        loop continue until the event queue has been
        emptied.
        """
        #wait for market open...
        cur_time = datetime.utcnow().time()
        if cur_time < self.mkt_open:
            sleep_time = datetime.combine(date.today(), self.mkt_open) - datetime.combine(date.today(), cur_time)
            print(sleep_time.seconds)
            sleep(sleep_time.seconds)   
                   
        self.twsclient.run()
        self.price_handler.start_request_data()
        time_now = datetime.utcnow()
        while time_now <= self.trading_end:
            if not self.mkt_open <= time_now.time() <= self.mkt_close:
                self.wait_until_market_open()

            self.price_handler.get_next()
            self.price_handler.check_bar_interruption()
            self.broker.get_fill_event()
            try:                
                event = self.events_queue.get(False)
            except queue.Empty:
                pass            
            else:
                day = datetime.fromtimestamp(event.timestamp, timezone.utc).date()
                if self.previous_day is None:
                    self.previous_day = day
                elif day > self.previous_day:
                    self.statistics.update(self.previous_day, self.portfolio.get_asset_val())
                    self.portfolio.save_to_db(self.previous_day)
                    self.previous_day = day

                if event is not None:
                    if event.type == EventType.BAR:
                        self.strategy.calculate_signal(event)
                        self.portfolio.on_bar(event)                 
                    elif event.type == EventType.SIGNAL:
                        self.order_handler.create_order(event)
                    elif event.type == EventType.ORDER:
                        self.broker.execute_order(event)
                    elif event.type == EventType.FILL:
                        self.portfolio.on_fill(event)
                    else:
                        raise NotImplementedError("Unsupported event.type '%s'" % event.type)

            time_now = datetime.utcnow()

        self.statistics.update(self.previous_day, self.portfolio.get_asset_val())
        self.portfolio.save_to_db(self.previous_day)
        print("Market closed!", datetime.utcnow())


    def wait_until_market_open(self):
        print("cancelling existing subscribtion...")
        for i in range(0, len(self.twsclient.contracts_list)):
                self.twsclient.cancelRealTimeBars(i)
        self.twsclient.realtime_subscribed = False
        sleep(1)
        print("disconnect tws...")
        self.twsclient.disconnect()
        #sleep for market open again 
        cur_time = datetime.utcnow().time()
        day_now = datetime.utcnow().date()
        next_day = day_now + timedelta(days=1)
        print("day_now is ", day_now)
        print("next day is ", next_day)
        if next_day.isoweekday() == 6: #saturday
            #wait next Monday trading day
            print("next day is SAT...")
            next_day += timedelta(days=2)   
        sleep_time = datetime.combine(next_day, self.mkt_open) - datetime.combine(day_now, cur_time)
        print("sleep", sleep_time.total_seconds(), " seconds for market open...")       
        sleep(sleep_time.total_seconds())

        print("testing network connection...")
        while not check_ping():
            pass
        print("network is ok!")
        print("connecting to tws...")
        self.twsclient.connect("127.0.0.1", 7497, clientId=0)
        #wait for connecting to tws 
        while not self.twsclient.isConnected():
            pass
        print("reconnection is successful!")
        self.twsclient.run() 
        print("resubscribe data...")
        print("current time:", datetime.utcnow().time())
        self.twsclient.resubscribe_RealTimeBars()
        while not self.twsclient.realtime_subscribed:
            pass             


    def start_trading(self, testing=False):
        """
        Runs either a backtest or live session, and outputs performance when complete.
        """
        self.run_session()
        print("---------------------------------")
        print('Ending cash: ' + str(self.portfolio.cash))
        print('Ending market value: ' + str(self.portfolio.market_value))
        print('Ending asset value: ' + str(self.portfolio.get_asset_val()))
        print('Ending Portfolio:')
        results = self.statistics.get_results()
        print("---------------------------------")
        print("Strategy:", self.strategy)
        print("Sharpe Ratio: %0.2f" % results["sharpe_ratio"])
        print(
            "Max Drawdown: %0.2f%%" % (
                results["max_drawdown"] * 100.0
            )
        )
        print("Return: %0.2f%%" % results["return"])
        print("Trading ends")
        self.statistics.plot_results()


#set up     
events_queue = queue.Queue()       

init_asset_val = 10000
session_type = SessionType.LIVE

twsclient = TWSClient()
twsclient.connect("127.0.0.1", 7497, clientId=0)

try:
    db_client = connect(host = "127.0.0.1", user = "root", password = "password", database="tradingsystem")
except Error as e:
    print(e)

mkt_open = time(13,30)
mkt_close = time(20,0)
# mkt_open = time(8,30)
# mkt_close = time(20,0)

symbol_list = ['AMZN']
#symbol_list = ['USD/JPY']


ib_bar_handler = IBRealTimeBarHandler(twsclient, symbol_list, 60, 
                                      "MIDPOINT", True, events_queue, 
                                      db_client)

portfolio = Portfolio(init_asset_val, db_client)
max_order_handler = MaxOrderHandler(portfolio, events_queue, session_type, db_client)

sma_crossover = SMACrossover(symbol_list, 1, 2, events_queue, session_type, portfolio)
macdrsi = MACDRSI(symbol_list, 12, 26, 9, 14, events_queue, session_type, portfolio, db_client)

ib_broker = IBBroker(twsclient, events_queue, symbol_list, db_client)

stat = Statistics(init_asset_val)


trading_end = datetime(2022,7,30,20,0)
trading_session = TradingSession(twsclient, ib_bar_handler, sma_crossover, portfolio, 
                                 max_order_handler, ib_broker, events_queue, 
                                 mkt_open, mkt_close, trading_end, stat)

trading_session.start_trading()

print("disconnecting tws...")
twsclient.disconnect()


