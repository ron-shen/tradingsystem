#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 29 21:09:43 2021

@author: ron
"""

from datetime import datetime, timezone
import time
from enum import Enum
from tracemalloc import start
import os
import subprocess

SessionType = Enum("SessionType", "LIVE BACKTEST")

def get_cur_time(event, session_type):
    if session_type == SessionType.BACKTEST:
        return event.timestamp
    
    if session_type ==  SessionType.LIVE:
        #return datetime.now(timezone.utc)
        return int(time.time())


class RealTimeBarError(Exception):
    pass


class Bar():
    def __init__(
        self, start_time, end_time,
        open_price, high_price, low_price,
        close_price, volume, wap, count
        ):
        """
        Initialises the BarEvent.
        Parameters:
        timestamp - The timestamp of the Bar event generated (i.e. timestamp of a bar)
        ticker - The ticker symbol, e.g. 'GOOG'.
        open_price - The opening price of the bar
        high_price - The high price of the bar
        low_price - The low price of the bar
        close_price - The close price of the bar
        volume - The volume of trading within the bar
        """
        self.start_time = start_time
        self.end_time = end_time
        self.open_price = open_price
        self.high_price = high_price
        self.low_price = low_price
        self.close_price = close_price
        self.volume = volume
        self.wap = wap
        self.count = count

    def __str__(self):
        format_str = "Start: %s, End: %s, " \
            "Open: %s, High: %s, Low: %s, Close: %s, Volume: %s ,WAP %s, Count %s" % (
                str(self.start_time), str(self.end_time),
                str(self.open_price), str(self.high_price), 
                str(self.low_price), str(self.close_price),
                str(self.volume), str(self.wap), str(self.count)
            )
        return format_str

    def __repr__(self):
        return str(self)


class Error():
    def __init__(self, time, errorCode, errorString):
        self.time = time
        self.code = errorCode
        self.string = errorString


def check_ping():
    proc = subprocess.Popen(
        ['ping', '-q', '-c', '3', "8.8.8.8"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL) 
    proc.wait()
    # and then check the response...
    if proc.returncode == 0:
        return True
    else:
        return False
