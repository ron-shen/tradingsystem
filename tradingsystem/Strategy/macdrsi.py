from .base import AbstractStrategy
from ..technical_indicators.macd import MACD
from ..technical_indicators.rsi import RSI
from ..event.event import SignalEvent, OrderType, Direction
from ..common import get_cur_time
from enum import Enum
from datetime import datetime, timezone

GO = Enum("GO", "LONG SHORT NONE")  

class MACDRSI(AbstractStrategy):
    #to indicate what kind of direction we want to trade
           
    def __init__(self, ticker_list, macd_shortPeriod, macd_longPeriod,
                 macd_signalPeriod, rsi_period, 
                 event_queue, session_type, portfolio, db_client=None
        ):
        """
        Parameters
        ----------
        tickers_data : dict: {key:string, value: list }
                       key is the ticker symbol, e.g. 'GOOG'
                       list[0] stores MACD object.
                       list[1] stores RSI object.
                       
        session_type: 'backtest' or 'live'
        -------

        """
        self.db_client = db_client
        self.macd_shortPeriod = macd_shortPeriod
        self.macd_longPeriod = macd_longPeriod
        self.macd_signalPeriod = macd_signalPeriod
        self.rsi_period = rsi_period
        self.tickers_data = self._subscribe_ticker(ticker_list)
        self.event_queue = event_queue
        self.session_type = session_type
        self.event_queue = event_queue
        self.session_type = session_type
        self.portfolio = portfolio
        self.go_flag = GO.NONE


    def calculate_signal(self, bar_event):
        ticker_data = self.tickers_data[bar_event.ticker]            
        ticker_data[0].update(bar_event.close_price)
        ticker_data[1].update(bar_event.close_price)
        #Both MACD and RSI have value
        if ticker_data[0] and ticker_data[1] and len(ticker_data[0].data_store[2]) >= 2:                            
            macd = ticker_data[0].lastest_val
            rsi = ticker_data[1].lastest_val
            ticker_info = self.portfolio.get_fin_instrument(bar_event.ticker)
            if self.db_client is not None:
                self.save_to_db_ta(bar_event, macd, rsi)
            #want to enter long/short position
            if ticker_info is None:           
                if self.go_flag != GO.SHORT and self._long_signal(bar_event, macd, rsi, ticker_data):
                    cur_time = get_cur_time(bar_event, self.session_type)
                    signal_event = SignalEvent(cur_time, bar_event.ticker,
                                                OrderType.MARKET, Direction.LONG, 
                                                bar_event.close_price)
                    self.event_queue.put(signal_event)
                    if self.db_client is not None:
                        self.save_to_db_signal(signal_event)                   
                    print(signal_event)
                                            
                if self.go_flag != GO.LONG and self._short_signal(bar_event, macd, rsi, ticker_data):
                    cur_time = get_cur_time(bar_event, self.session_type)                    
                    signal_event = SignalEvent(cur_time, bar_event.ticker,
                                                OrderType.MARKET, Direction.SHORT, 
                                                bar_event.close_price)  
                    self.event_queue.put(signal_event)
                    if self.db_client is not None:
                        self.save_to_db_signal(signal_event)                       
                    print(signal_event)  

            else:                                            
                #want to exit long position                                                  
                if ticker_info.POS > 0 and self._exit_signal_long(bar_event, macd, rsi, ticker_data):                  
                    cur_time = get_cur_time(bar_event, self.session_type)
                    signal_event = SignalEvent(cur_time, bar_event.ticker,
                                            OrderType.MARKET, Direction.SHORT, 
                                            bar_event.close_price)                    
                    self.event_queue.put(signal_event)  
                    if self.db_client is not None:
                        self.save_to_db_signal(signal_event)                       
                    print(signal_event)
                            
                #want to exit short position            
                elif ticker_info.POS < 0 and self._exit_signal_short(bar_event, macd, rsi, ticker_data):              
                    cur_time = get_cur_time(bar_event, self.session_type)
                    signal_event = SignalEvent(cur_time, bar_event.ticker,
                                            OrderType.MARKET, Direction.LONG, 
                                            bar_event.close_price)                                                
                    self.event_queue.put(signal_event) 
                    if self.db_client is not None:
                        self.save_to_db_signal(signal_event)                       
                    print(signal_event)


    def save_to_db_ta(self, bar_event, macd, rsi):
        query = "INSERT INTO MACDRSI VALUES (%s, %s, %s, %s, %s, %s)"
        timestamp_converted = datetime.fromtimestamp(bar_event.timestamp, timezone.utc)
        data = (timestamp_converted, bar_event.ticker, macd[0], macd[1], macd[2], rsi)
        #print(data)
        cursor = self.db_client.cursor()
        cursor.execute(query, data)
        self.db_client.commit()   

                
    def _subscribe_ticker(self, ticker_list):
        tickers_data = {}
        for ticker in ticker_list:
            data = []           
            macd = MACD(self.macd_shortPeriod, self.macd_longPeriod, self.macd_signalPeriod)
            rsi = RSI(self.rsi_period)  
            data = [macd, rsi]
            tickers_data[ticker] = data

        return tickers_data  


    def _long_signal(self, bar_event, macd, rsi, ticker_data):
        rsi_condition = rsi <= 30
        if self.go_flag == GO.NONE and rsi_condition:
            #now we can wait for the macd crosses above signal line
            #print("Want long at:", bar_event.timestamp)
            self.go_flag = GO.LONG
            #print("GO Long Flag set")
            return False

        if self.go_flag == GO.LONG:           
            prev_macd_histogram = ticker_data[0].data_store[2][-2]
            macd_histogram = macd[2]
            #bullish crossover
            if macd_histogram > 0  and prev_macd_histogram <= 0 and rsi > 30: 
                self.go_flag = GO.NONE
                #print("Bullish crossover")
                return True 

            elif rsi >= 70:
                #print("reset long at:", bar_event.timestamp)
                self.go_flag = GO.NONE
                return False              
       
        return False


    def _short_signal(self, bar_event, macd, rsi, ticker_data):
        rsi_condition = rsi >= 70
        if self.go_flag == GO.NONE and rsi_condition:
            #now we can wait for the macd crosses above signal line
            #print("Want short at:", bar_event.timestamp)
            #print("GO Short Flag set")
            self.go_flag = GO.SHORT
            return False

        if self.go_flag == GO.SHORT:
            prev_macd_histogram = ticker_data[0].data_store[2][-2]
            macd_histogram = macd[2]
            #bearish crossover 
            if macd_histogram < 0  and prev_macd_histogram >= 0 and rsi < 70: 
                self.go_flag = GO.NONE
                #print("Bearish corssover")
                return True 

            elif rsi <= 30:
                #print("reset short at:", bar_event.timestamp)
                self.go_flag = GO.NONE
                return False

        return False


    def _exit_signal_long(self, bar_event, macd, rsi, ticker_data):
        macd_histogram = macd[2]
        prev_macd_histogram = ticker_data[0].data_store[2][-2]
        exit_long = macd_histogram < 0  and prev_macd_histogram >= 0
        #print("exit long")
        #if exit_long:
            #print("exit long")
        return exit_long   


    def _exit_signal_short(self, bar_event, macd, rsi, ticker_data):
        macd_histogram = macd[2]
        prev_macd_histogram = ticker_data[0].data_store[2][-2]
        exit_short = macd_histogram > 0  and prev_macd_histogram <= 0
        #if exit_short:
            #print("exit short")        
        #print("exit short")
        return exit_short


    def stop_loss_trigger(self, bar_event):
        pass
        # """
        # stop loss is trigger if the current price is 
        # lower(for long)/higher(for short) than
        # the low of entry candle
        # """
        # invested_type = self.tickers_data[bar_event.ticker][2]
        # if invested_type == InvestedType.LONG and bar_event.close_price < self.stop_price:
        #     print("Long Stop loss:", bar_event.timestamp)
        #     return True

        # if invested_type == InvestedType.SHORT and bar_event.close_price > self.stop_price:
        #     print("Short Stop loss:", bar_event.timestamp)
        #     return True

        # return False      



    def get_ticker(self):
        return self.tickers_data
    
    
    def __str__(self):
        return "MACD-RSI Strategy"
    
