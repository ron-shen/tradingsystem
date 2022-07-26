from Order_Handler.base import AbstractOrderHandler
from Event.event import OrderType, OrderEvent
from common import get_cur_time
import math


class MaxOrderHandler(AbstractOrderHandler):
    """
    create all-in/all-out order
    TO-DO: Reject the order when cash is not enough 
    """
    def __init__(self, portfolio, event_queue, session_type, db_client=None):
        self.db_client = db_client
        self.portfolio = portfolio
        self.event_queue = event_queue
        self.session_type = session_type
        self.db_client = db_client

    def create_order(self, signal_event):
        fin_instrument = self.portfolio.get_fin_instrument(signal_event.ticker)
        #all-out if it has a position already 
        if fin_instrument is not None:
            quantity = int(abs(fin_instrument.POS))

        #all-in if it does not have any position
        else:   
            if signal_event.order_type == OrderType.MARKET:
                quantity = math.floor(self.portfolio.cash / signal_event.bar_closing_price)
                
            elif signal_event.order_type == OrderType.LIMIT:
                quantity = math.floor(self.portfolio.cash / signal_event.entry_price)
            
        cur_time = get_cur_time(signal_event, self.session_type)
        ticker = signal_event.ticker
        order_type = signal_event.order_type
        direction = signal_event.direction
        entry_price = signal_event.entry_price
        order_event = OrderEvent(cur_time, ticker, order_type, 
                                 direction, quantity, entry_price)
        print(order_event)
        self.event_queue.put(order_event)
        
        if self.db_client is not None:
            self._save_to_db(order_event)           
    