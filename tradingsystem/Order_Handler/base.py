from abc import ABC, abstractmethod
from datetime import datetime, timezone

class AbstractOrderHandler(ABC):
    """
    AbstractOrderHandler is an abstract base class 
    for all order handler class

    It receives SignalEvent and then create OrderEvent
    """
    @abstractmethod
    def create_order(self, signal_event):
        pass
    

    def _save_to_db(self, order_event):
        query = ("INSERT INTO OrderEvent (Datetime, Ticker, Order_Type, Direction, Quantity, Entry_Price)"
                "VALUES (%s, %s, %s, %s, %s, %s)"
        )
        timestamp_converted = datetime.fromtimestamp(order_event.timestamp, timezone.utc)
        data = (timestamp_converted, order_event.ticker, order_event.order_type.name, order_event.direction.name, 
                order_event.quantity, order_event.entry_price)
        cursor = self.db_client.cursor()
        cursor.execute(query, data)
        self.db_client.commit()  

    
    
    
    

    
    
