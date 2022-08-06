from ast import Pass
from datetime import datetime, timedelta, time
import queue
import unittest
from IBTWS.twsclient import TWSClient
from Event.event import BarEvent
from common import Bar
from ibapi.common import BarData
from threading import Condition


def construct_BarData(time, open, high, low, close, volume, wap, count):
    bar = BarData()
    bar.date = time
    bar.open = open
    bar.high = high
    bar.low = low
    bar.close = close
    bar.volume = volume
    bar.wap = wap
    bar.barCount = count
    return bar


class TestTWSClient(unittest.TestCase):
    #test the fuctions in twsclient and twswrapper
    def setUp(self):
        self.lastest_bar_event = queue.Queue()
        self.twsclient = TWSClient("127.0.0.1", 7497, 0)
        self.twsclient.last_bar_time = 0 
        self.twsclient._bars = {0: BarEvent(None, "AAPL", None, -1, 999999, None, 0 )}
        self.twsclient.lastest_bar_event = queue.Queue()
        self.twsclient.timeframe = 60
        self.twsclient.realtime_subscribed = False
        
        self.bar_stream = []
        self.bar_stream.append(Bar(1644662475, 1644662480, 2, 4, 2, 3, 100, -1, -1))
        self.bar_stream.append(Bar(1644662480, 1644662485, 3, 5, 2, 4, 100, -1, -1)) 
        self.bar_stream.append(Bar(1644662485, 1644662490, 4, 5, 3, 3, 100, -1, -1)) 
        self.bar_stream.append(Bar(1644662490, 1644662495, 3, 4, 3, 2, 100, -1, -1)) 
        self.bar_stream.append(Bar(1644662495, 1644662500, 2, 7, 2, 7, 100, -1, -1)) 
        self.bar_stream.append(Bar(1644662500, 1644662505, 7, 10, 7, 9, 100, -1, -1)) 
        self.bar_stream.append(Bar(1644662505, 1644662510, 9, 13, 1, 12, 100, -1, -1)) 
        self.bar_stream.append(Bar(1644662510, 1644662515, 12, 15, 12, 14, 100, -1, -1)) 
        self.bar_stream.append(Bar(1644662515, 1644662520, 14, 14, 9, 10, 100, -1, -1)) 
        self.bar_stream.append(Bar(1644662520, 1644662525, 10, 11, 8, 9, 100, -1, -1)) 
        self.bar_stream.append(Bar(1644662525, 1644662530, 11, 11, 11, 11, 100, -1, -1))
        self.bar_stream.append(Bar(1644662530, 1644662535, 11, 12, 5, 10, 100, -1, -1))


    def test_construct_bar(self):
        #test whether a 1min candle bar can be correctly
        #constructed by streaming 5 sec candle bars
        aapl_bar = self.twsclient._bars[0]
        first_bar_time = 1644662475
        volume = 0
        max_price = float('-inf')
        min_price = float('inf')
        open_price = self.bar_stream[0].open_price
        
        for i in range(len(self.bar_stream)):
            self.twsclient._construct_bar(0, self.bar_stream[i])
            max_price = max(self.bar_stream[i].high_price, max_price)
            min_price = min(self.bar_stream[i].low_price, min_price)                              
            volume += self.bar_stream[i].volume
            
            if i != len(self.bar_stream) - 1:
                #candle bar expected at each 5s bar coming in
                expected_bar = BarEvent(first_bar_time, "AAPL", open_price, max_price, min_price, None, volume)
                self.assertEqual(aapl_bar, expected_bar)
            #last bar, fill the close price
            else:
                constructed_bar = self.twsclient.lastest_bar_event.get()
                expected_bar = BarEvent(first_bar_time, "AAPL", 2, 15, 1, 10, 1200)
                self.assertEqual(constructed_bar, expected_bar)
                
            self.assertEqual(self.twsclient.last_bar_time, self.bar_stream[i].end_time)
        
        #test whether the next new 1min bar can be constructed correctly
        #after receiving the 5 sec bar
        bar = Bar(1644662535, 1644662540, 10, 15, 10, 11, 100, -1, -1)       
        self.twsclient._construct_bar(0, bar)
        expected_bar = BarEvent(1644662535, "AAPL", 10, 15, 10, None, 100)
        self.assertEqual(aapl_bar, expected_bar)
        self.assertEqual(self.twsclient.last_bar_time, 1644662540)
        
       
    def test_construct_bar_missing_end(self):
        #test whether it can function normally 
        # if there is a 5 sec bar missing at the end
        aapl_bar = self.twsclient._bars[0]
        first_bar_time = 1644662475
        #pop out the last bar to simulate the last 5sec bar is missing
        self.bar_stream.pop()
        #the next 5sec bar received is the start of the next 1min bar
        self.bar_stream.append(Bar(1644662535, 1644662540, 11, 20, 5, 9, 100, -1, -1))
        volume = 0
        max_price = float('-inf')
        min_price = float('inf')
        open_price = self.bar_stream[0].open_price
        
        for i in range(len(self.bar_stream)):
            self.twsclient._construct_bar(0, self.bar_stream[i])
            max_price = max(self.bar_stream[i].high_price, max_price)
            min_price = min(self.bar_stream[i].low_price, min_price)                              
            volume += self.bar_stream[i].volume
            
            if i != len(self.bar_stream) - 1:
                expected_bar = BarEvent(first_bar_time, "AAPL", open_price, max_price, min_price, None, volume)
                self.assertEqual(aapl_bar, expected_bar)
            #last bar, fill the close price
            else:
                constructed_bar = self.twsclient.lastest_bar_event.get()
                expected_bar = BarEvent(first_bar_time, "AAPL", 2, 20, 1, 9, 1200)
                self.assertEqual(constructed_bar, expected_bar)
                
            self.assertEqual(self.twsclient.last_bar_time, self.bar_stream[i].end_time)
            
        #test whether the next new 1min bar can be constructed correctly
        #after receiving the 5 sec bar    
        bar = Bar(1644662540, 1644662545, 10, 15, 10, 11, 100, -1, -1)       
        self.twsclient._construct_bar(0, bar)
        expected_bar = BarEvent(1644662540, "AAPL", 10, 15, 10, None, 100)
        self.assertEqual(aapl_bar, expected_bar)
        

    def test_construct_bar_missing_middle(self):
        #test whether it can function normally 
        # if there are some 5 sec bars missing during the construction
        aapl_bar = self.twsclient._bars[0]
        first_bar_time = 1644662475
        #missming middle
        #remove Bar(1644662505, 1644662510, 9, 13, 1, 12, 100, -1, -1)
        del self.bar_stream[6]
        volume = 0
        max_price = float('-inf')
        min_price = float('inf')
        open_price = self.bar_stream[0].open_price       
        
        for i in range(len(self.bar_stream)):
            self.twsclient._construct_bar(0, self.bar_stream[i])
            max_price = max(self.bar_stream[i].high_price, max_price)
            min_price = min(self.bar_stream[i].low_price, min_price)                              
            volume += self.bar_stream[i].volume
            
            if i != len(self.bar_stream) - 1:
                expected_bar = BarEvent(first_bar_time, "AAPL", open_price, max_price, min_price, None, volume)
                self.assertEqual(aapl_bar, expected_bar)
            #last bar, fill the close price
            else:
                constructed_bar = self.twsclient.lastest_bar_event.get()
                expected_bar = BarEvent(first_bar_time, "AAPL", 2, 15, 2, 10, 1100)
                self.assertEqual(constructed_bar, expected_bar)
                
            self.assertEqual(self.twsclient.last_bar_time, self.bar_stream[i].end_time)


    def test_historicalData(self):
        #test whether the missing bar can be retrived
        #and be construced sucessfully when there is a network interruption
        #assume network interruption at 1644662537
        #and network restore at 1644662600 
        #then it gets 5 sec bars from 1644662535 to 1644662600
        aapl_bar = self.twsclient._bars[0]
        for bar in self.bar_stream:
            self.twsclient._construct_bar(0, bar)

        self.twsclient.lastest_bar_event.get()
        #network interruption at 1644662537 and restore at 1644662600
        backfill_bars = []
        backfill_time = []
        start_time = datetime.strptime("20220212 10:42:15", "%Y%m%d  %H:%M:%S")
        
        for _ in range(13):
            backfill_time.append(start_time.strftime("%Y%m%d %H:%M:%S"))
            start_time += timedelta(seconds=5)
             
        backfill_bars.append(construct_BarData(backfill_time[0], 10, 15, 9, 9, 100, -1, -1)) #20220212 10:42:15 (1644662535)
        backfill_bars.append(construct_BarData(backfill_time[1], 9, 10, 9, 9, 100, -1, -1)) #20220212 10:42:20 (1644662540)
        backfill_bars.append(construct_BarData(backfill_time[2], 9, 20, 15, 18, 100, -1, -1)) #20220212 10:42:25 (1644662545)
        backfill_bars.append(construct_BarData(backfill_time[3], 18, 20, 18, 20, 100, -1, -1)) #20220212 10:42:30 (1644662550)
        backfill_bars.append(construct_BarData(backfill_time[4], 20, 25, 19, 23, 100, -1, -1)) #20220212 10:42:35 (1644662555)
        backfill_bars.append(construct_BarData(backfill_time[5], 23, 23, 23, 23, 100, -1, -1)) #20220212 10:42:40 (1644662560)
        backfill_bars.append(construct_BarData(backfill_time[6], 23, 23, 18, 22, 100, -1, -1)) #20220212 10:42:45 (1644662565)
        backfill_bars.append(construct_BarData(backfill_time[7], 22, 30, 3, 25, 100, -1, -1)) #20220212 10:42:50 (1644662570)
        backfill_bars.append(construct_BarData(backfill_time[8], 25, 25, 15, 17, 100, -1, -1)) #20220212 10:42:55 (1644662575)
        backfill_bars.append(construct_BarData(backfill_time[9], 17, 18, 15, 15, 100, -1, -1)) #20220212 10:43:00 (1644662580)
        backfill_bars.append(construct_BarData(backfill_time[10], 15, 19, 10, 12, 100, -1, -1)) #20220212 10:43:05 (1644662585)
        backfill_bars.append(construct_BarData(backfill_time[11], 12, 15, 12, 11, 100, -1, -1)) #20220212 10:43:10 (1644662590)
        backfill_bars.append(construct_BarData(backfill_time[12], 11, 18, 14, 17, 100, -1, -1)) #20220212 10:43:15 (1644662595)

        for i in range(len(backfill_bars)):
            self.twsclient.historicalData(0, backfill_bars[i])   
        constructed_bar = self.twsclient.lastest_bar_event.get()
        
        expected_bar = BarEvent(1644662535, "AAPL", 10, 30, 3, 11, 1200)
        self.assertEqual(constructed_bar, expected_bar)
        expected_bar = BarEvent(1644662595, "AAPL", 11, 18, 14, None, 100)
        self.assertEqual(aapl_bar, expected_bar)
     

    def test_construct_bar_end(self):
        """
        test if the bar is constructed when market ends.
        """
        self.twsclient.end_time = 1644662530
        self.twsclient.lastest_bar_event = queue.Queue()
        self.bar_stream.pop()
        for i in range(len(self.bar_stream)):
            self.twsclient._construct_bar(0, self.bar_stream[i])

        self.assertEqual(self.twsclient.lastest_bar_event.qsize(), 1)

        


if __name__ == '__main__':
    unittest.main(verbosity=2)  