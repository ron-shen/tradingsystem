from .base import AbstractBroker
from ..event.event import FillEvent, OrderType

class IBSimulatedBroker(AbstractBroker):
    """
    The simulated execution handler for Interactive Brokers
    converts all order objects into their equivalent fill
    objects automatically without latency, slippage or
    fill-ratio issues.
    """
    def __init__(self, event_queue, data_handler, db_client=None):
        self.db_client = db_client
        self.event_queue = event_queue
        self.unfilled_order = {} #store limit order that cannot yet match the market price 
        self.data_handler = data_handler
 
    
    def execute_order(self, order_event):
        if order_event.order_type == OrderType.MARKET:
            timestamp = order_event.timestamp
            ticker = order_event.ticker
            direction = order_event.direction
            exchange = "Test Exchange"
            price = self.data_handler.get_last(ticker)
            quantity = order_event.quantity
            commission = 1
            fill_event = FillEvent(timestamp, ticker, direction,
                                   exchange, price, quantity, commission)
            self.event_queue.put(fill_event)
            print(fill_event)

                         
        elif order_event.order_type == OrderType.LIMIT:
            pass
