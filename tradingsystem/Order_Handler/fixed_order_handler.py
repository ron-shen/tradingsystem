from Order_Handler.base import AbstractOrderHandler
from Event.event import OrderEvent
from common import get_cur_time


class FixedOrderHandler(AbstractOrderHandler):
    """
    TO-DO: Reject the order when cash is not enough 
    """
    def __init__(self, quantity, portfolio, event_queue, session_type, db_client=None):
        self.db_client = db_client
        self.fixed_quantity = quantity
        self.portfolio = portfolio
        self.event_queue = event_queue
        self.session_type = session_type

    
    def create_order(self, signal_event):
        cur_time = get_cur_time(signal_event, self.session_type)
        ticker = signal_event.ticker
        order_type = signal_event.order_type
        direction = signal_event.direction
        entry_price = signal_event.entry_price
        order_event = OrderEvent(cur_time, ticker, order_type, 
                                 direction, self.fixed_quantity, entry_price)
        self.event_queue.put(order_event)
        print(order_event)


