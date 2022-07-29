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
import time
from datetime import datetime, timezone, date, timedelta
from common import SessionType, check_ping
from mysql.connector import connect, Error
from Trading_Schedule.fx_schedule import FXSchedule


class TradingSession:
    """
    Enscapsulates the settings and components for
    carrying out a live trading session through Interactive Brokers.
    """    
    def __init__(
        self, twsclient, price_handler, 
        strategy, portfolio, 
        order_handler, broker, events_queue,
        trading_schedule, trading_end, statistics=None, 
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
        self.trading_end = trading_end.replace(tzinfo=timezone.utc).timestamp()
        self.trading_schedule = trading_schedule

             
    def run_session(self):
        """
        Carries out an infinite while loop that polls the
        events queue and directs each event to either the
        strategy component of the execution handler. The
        loop continue until the event queue has been
        emptied.
        """
        while time.time() <= self.trading_end:
            today = date.today()            
            if not self.trading_schedule.calendar.is_holiday(today):
                start, end = self.trading_schedule.get_trading_hours(today)
                print("start: ", start)
                print("end: ", end)
                cur_time = time.time()
                if cur_time < start:
                    sleep_time = start - cur_time
                    time.sleep(sleep_time)                  
                self.twsclient.run()
                self.price_handler.request_data()
                while start <= time.time() <= end:
                    self.price_handler.get_next()
                    # self.price_handler.check_bar_interruption()
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
            self._reset()       
            self._sleep_next_open_day(today)

        
    def _reset(self):
        if self.twsclient.realtime_subscribed:
            print("cancelling existing subscribtion...")
            for i in range(len(self.twsclient.contracts_list)):
                    self.twsclient.cancelRealTimeBars(i)
            self.twsclient.realtime_subscribed = False
            time.sleep(1)
            print("disconnect tws...")
            self.twsclient.disconnect()        
         
         
    def _sleep_next_open_day(self, today):
        next_day = today + timedelta(days=1)
        next_start, _ = self.trading_schedule.get_trading_hours(next_day)
        cur_time = time.time()
        sleep_time = next_start - cur_time
        print(sleep_time)
        time.sleep(sleep_time)
        
        
    def start_trading(self, testing=False):
        """
        Runs either a backtest or live session, and outputs performance when complete.
        """
        self.run_session()
        print("disconnecting tws...")
        self.twsclient.disconnect()
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
    raise Exception(e)


trading_schedule = FXSchedule(2022)
#symbol_list = ['AMZN']
symbol_list = ['USD/JPY']


ib_bar_handler = IBRealTimeBarHandler(twsclient, symbol_list, 60, 
                                      "MIDPOINT", True, events_queue, 
                                      db_client)

portfolio = Portfolio(init_asset_val, db_client)
max_order_handler = MaxOrderHandler(portfolio, events_queue, session_type, db_client)

sma_crossover = SMACrossover(symbol_list, 1, 2, events_queue, session_type, portfolio)
macdrsi = MACDRSI(symbol_list, 12, 26, 9, 14, events_queue, session_type, portfolio, db_client)

ib_broker = IBBroker(twsclient, events_queue, symbol_list, db_client)

stat = Statistics(init_asset_val)


trading_end = datetime(2022,12,31,21,0)
trading_session = TradingSession(twsclient, ib_bar_handler, sma_crossover, portfolio, 
                                 max_order_handler, ib_broker, events_queue, 
                                 trading_schedule, trading_end, stat)

trading_session.start_trading()



