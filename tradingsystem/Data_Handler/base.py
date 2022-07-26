from abc import ABC, abstractmethod
from datetime import datetime, timezone


class AbstractDataHandler(ABC):
    """
    AbstractDataHandler is an abstract base class for all 
    live and historical data handlers (e.g. Bar, Tick, Options, Futures...)
    """   
    @abstractmethod
    def get_next(self):
        pass
    
    
    def save_to_db(self, bar_event):
        query = ("INSERT INTO BarEvent (Datetime, Ticker, Open, High, Low, Close, Volume)"
                "VALUES (%s, %s, %s, %s, %s, %s, %s)"
        )
        timestamp_converted = datetime.fromtimestamp(bar_event.timestamp, timezone.utc)
        data = (timestamp_converted, bar_event.ticker, bar_event.open_price, bar_event.high_price, 
                bar_event.low_price, bar_event.close_price, bar_event.volume)
        cursor = self.db_client.cursor()
        cursor.execute(query, data)
        self.db_client.commit()   
    
    

