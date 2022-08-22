from .base import AbstractDataHandler
import yfinance as yf
import pandas as pd
from ..event.event import BarEvent


class HistoricalBarHandler(AbstractDataHandler):
    def __init__(self, tickers_data, event_queue, db_client=None):
        """
        Parameters
        ----------
        tickers_data : dict{key: ticker, value: dataframe}
        The dataframe must have the foramt below:
        Datetime object, Open, High, Low, Close, Volume
        """ 
        self.db_client = db_client
        self.bar_data = self._sort_tickers_data(tickers_data)
        self.event_queue = event_queue
        self.tickers_lastest_bar = {}
        
           
    def get_next(self):
        try:
            current_bar = next(self.bar_data)
            bar_event = self._create_bar_event(current_bar)
            self.tickers_lastest_bar[bar_event.ticker] = bar_event.close_price 
            self.event_queue.put(bar_event)
            print(bar_event)
            
        except StopIteration:
            raise StopIteration

            
    def get_last(self, ticker):
         """
         Returns the most recent closing price.
         """        
         if ticker in self.tickers_lastest_bar:
             return self.tickers_lastest_bar[ticker]  
         else:
            print("ticker doesn't exist")
            return None

                              
    def _sort_tickers_data(self, tickers_data):
        """
        sort tickers_data according to the date and
        store them in self.tickers_data
        """
        sorted_bar_data = pd.DataFrame()
        #add 'Ticker' column to respective data and then put it in
        #sorted_bar_data
        for ticker in tickers_data:
            tickers_data[ticker]['Ticker'] = ticker
            sorted_bar_data = pd.concat([sorted_bar_data, tickers_data[ticker]])           
        sorted_bar_data.sort_index(inplace=True)
        return sorted_bar_data.itertuples()
    
    
    def _create_bar_event(self, current_bar):
        timestamp = current_bar[0]
        open_price = current_bar[1]
        high_price = current_bar[2]
        low_price = current_bar[3]
        close_price = current_bar[4]
        volume = current_bar[5]
        ticker = current_bar[6]
        return BarEvent(timestamp, ticker, open_price, high_price,
                 low_price, close_price, volume)
    
        
    
           
def get_data_from_yahoo_finance(ticker, start_date, end_date, interval):  
    historical_bar_data = yf.download(ticker, start=start_date, 
                                  end=end_date, interval=interval)
    historical_bar_data.drop('Adj Close', inplace=True, axis=1)
    return historical_bar_data

    
def get_data_from_csv(csv_path):
    historical_bar_data = pd.read_csv(csv_path, index_col=0, parse_dates=True)
    return  historical_bar_data
    
    
    

    

