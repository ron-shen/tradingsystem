from enum import Enum

EventType = Enum("EventType", "BAR SIGNAL ORDER FILL")
OrderType = Enum("OrderType", "MARKET LIMIT") 
Direction = Enum("Direction", "LONG SHORT")


class Event:
    """
    Event is base class providing an interface for all subsequent
    (inherited) events, that will trigger further events in the
    trading infrastructure.
    """
    @property
    def get_event_type(self):
        return self.type.name


class BarEvent(Event):
    """
    Created by a DataHandler object.
    This is received by a Strategy object and Portfolio and acted upon.
    """
    def __init__(
        self, timestamp, ticker,
        open_price, high_price, low_price,
        close_price, volume
        ):
        """
        Initialises the BarEvent.
        Parameters:
        timestamp - The timestamp of the Bar Event generated (i.e. timestamp of a bar)
        ticker - The ticker symbol, e.g. 'GOOG'.
        open_price - The opening price of the bar
        high_price - The high price of the bar
        low_price - The low price of the bar
        close_price - The close price of the bar
        volume - The volume of trading within the bar
        """
        self.type = EventType.BAR
        self.timestamp = timestamp
        self.ticker = ticker
        self.open_price = open_price
        self.high_price = high_price
        self.low_price = low_price
        self.close_price = close_price
        self.volume = volume

    def __str__(self):
        format_str = "Type: %s, Time: %s, Ticker: %s, " \
            "Open: %s, High: %s, Low: %s, Close: %s, Volume: %s" % (
                str(self.type), str(self.timestamp), str(self.ticker),
                str(self.open_price), str(self.high_price), 
                str(self.low_price), str(self.close_price),
                str(self.volume)
            )
        return format_str

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.type == other.type and self.timestamp == other.timestamp and \
            self.ticker == other.ticker and self.open_price == other.open_price and \
                self.high_price == other.high_price and self.low_price == other.low_price and \
                    self.close_price == other.close_price and self.volume == other.volume



class SignalEvent(Event):
    """
    Created by a Strategy object.
    This is received by a Portfolio object and acted upon.
    """
    def __init__(self, timestamp, ticker, order_type, 
                 direction, bar_closing_price, entry_price=None
                 ):
        """
        Initialises the SignalEvent.
        Parameters:
        timestamp - timestamp of trading signal generated
        ticker - The ticker symbol, e.g. 'GOOG'.
        order_type - Market order or Limit order
        direction - 'LONG', 'SHORT', 'LONG_EXIT' or 'SHORT_EXIT'
        entry_price - entry price of the ticket, it should be None if 
                      it is a market order
        bar_closing_price - used by Position Handler to determine the number of
                            shares should be bought if it is market order.
        """
        self.type = EventType.SIGNAL
        self.timestamp = timestamp
        self.ticker = ticker
        self.order_type = order_type
        self.direction = direction
        self.bar_closing_price = bar_closing_price
        self.entry_price = entry_price
        #self.entry_price_range = entry_price_range
        
        
    def __str__(self):
        format_str = "Type: %s, Time: %s, Ticker: %s, Order Type: %s, " \
            "Direction: %s, Entry price: %s, Closing price: %s" % (
                str(self.type), str(self.timestamp), str(self.ticker),
                str(self.order_type), str(self.direction), 
                str(self.entry_price), str(self.bar_closing_price)
            )
        return format_str

    def __repr__(self):
        return str(self)
        


class OrderEvent(Event):
    """
    Created by a Portfolio object.
    This is received by a Broker object and acted upon.
    """
    def __init__(self, timestamp, ticker, order_type, 
                 direction, quantity, entry_price=None
                 ):
        """
        Initialises the OrderEvent.
        Parameters:
        timestamp - timestamp of order event generated
        ticker - The ticker symbol, e.g. 'GOOG'.
        direction - 'LONG', 'SHORT', 'LONG_EXIT' or 'SHORT_EXIT'
        order_type - Market order or Limit order
        entry_price - entry price of the ticket, it should be None if 
                      it is a market order
        quantity - The quantity of shares to transact.
        """
        self.type = EventType.ORDER
        self.timestamp = timestamp
        self.ticker = ticker
        self.order_type = order_type
        self.direction = direction
        self.quantity = quantity
        self.entry_price = entry_price
        #self.entry_price_range = entry_price_range

    def __str__(self):
        format_str = "Type: %s, Time: %s, Ticker: %s, Order Type: %s, " \
            "Direction: %s, Entry price: %s, Quantity: %s" % (
                str(self.type), str(self.timestamp), str(self.ticker),
                str(self.order_type), str(self.direction), 
                str(self.entry_price), str(self.quantity)
            )
        return format_str

    def __repr__(self):
        return str(self)


class FillEvent(Event):
    """
    Created by a Broker object.
    This is received by a Portfolio object to update the portfolio
    """

    def __init__(
        self, timestamp, ticker,
        direction, exchange,
        price, quantity,
        commission
        ):
        """
        Initialises the FillEvent object.
        timestamp - The timestamp when the order was filled.
        ticker - The ticker symbol, e.g. 'GOOG'.
        direction - 'LONG', 'SHORT', 'LONG_EXIT' or 'SHORT_EXIT'
        quantity - The filled quantity.
        exchange - The exchange where the order was filled.
        price - The price at which the trade was filled
        commission - The brokerage commission for carrying out the trade.
        """
        self.type = EventType.FILL
        self.timestamp = timestamp
        self.ticker = ticker
        self.direction = direction
        self.exchange = exchange
        self.price = price
        self.quantity = quantity
        self.commission = commission
        
    def __str__(self):
        format_str = "Type: %s, Time: %s, Ticker: %s, " \
            "Direction: %s, Exchange: %s, Price: %s, " \
            "Quantity: %s, Commission: %s" % (
                str(self.type), str(self.timestamp), str(self.ticker),
                str(self.direction), str(self.exchange), 
                str(self.price), str(self.quantity), str(self.commission)
            )
        return format_str

    def __repr__(self):
        return str(self)
