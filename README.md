# TradingSystem
An event-driven backtest/realtime quantitative trading system.

# Installation
1. create a virtual environment
2. pip install tradingsystem

# Examples
For backtesting,
```
import queue
from tradingsystem.data_handler.historical_bar_handler import HistoricalBarHandler, get_data_from_csv, get_data_from_yahoo_finance
from tradingsystem.strategy.sma_crossover import SMACrossover
from tradingsystem.portfolio.portfolio import Portfolio
from tradingsystem.order_handler.max_order_handler import MaxOrderHandler
from tradingsystem.broker.simulated_broker import IBSimulatedBroker
from tradingsystem.statistics.statistics import Statistics
from tradingsystem.common import SessionType
from tradingsystem.simulated_trading_session import TradingSession

events_queue = queue.Queue()       
init_asset_val = 10000
tickers_data = {}
amzn = get_data_from_yahoo_finance("AMZN", "2022-01-01", "2022-05-01", "1d")
ticker_list = ['AMZN']
tickers_data['AMZN'] = amzn
historical_bar_handler = HistoricalBarHandler(tickers_data, events_queue)
portfolio = Portfolio(init_asset_val)
order_handler = MaxOrderHandler(portfolio, events_queue, SessionType.BACKTEST)
sma_crossover = SMACrossover(ticker_list, 10, 20, events_queue, SessionType.BACKTEST, portfolio)
simulated_broker = IBSimulatedBroker(events_queue, historical_bar_handler)
stat = Statistics(init_asset_val)
trading_session = TradingSession(historical_bar_handler, sma_crossover, portfolio, 
                                 order_handler ,simulated_broker, events_queue, stat)
#start backtest
trading_session.start_trading()
```

For live trading in IB,
1. Ppen Trader Workstation (TWS) or IB Gateway
2. Change timezone to UTC in options
3. Run the code below
```
import queue
from tradingsystem.data_handler.ib_real_time import IBRealTimeBarHandler
from tradingsystem.strategy.sma_crossover import SMACrossover
from tradingsystem.order_handler.max_order_handler import MaxOrderHandler
from tradingsystem.portfolio.portfolio import Portfolio
from tradingsystem.broker.ib_broker import IBBroker
from tradingsystem.statistics.statistics import Statistics
from tradingsystem.ibtws.twsclient import TWSClient
from tradingsystem.common import SessionType
from tradingsystem.trading_schedule.fx_schedule import FXSchedule
from datetime import datetime
from tradingsystem.ib_trading_session import TradingSession

#set up     
events_queue = queue.Queue()       
init_asset_val = 10000 #in USD
session_type = SessionType.LIVE
twsclient = TWSClient("127.0.0.1", 7497, 0)
trading_schedule = FXSchedule(2022)
symbol_list = ['EUR/USD']
ib_bar_handler = IBRealTimeBarHandler(twsclient, symbol_list, 300, 
                                      "MIDPOINT", True, events_queue, 
                                      )
portfolio = Portfolio(init_asset_val)
max_order_handler = MaxOrderHandler(portfolio, events_queue, session_type)
sma_crossover = SMACrossover(symbol_list, 10, 20, events_queue, session_type, portfolio)
ib_broker = IBBroker(twsclient, events_queue, symbol_list)
stat = Statistics(init_asset_val)
trading_end = datetime(2022,12,31, 0, 00)
trading_session = TradingSession(twsclient, ib_bar_handler, sma_crossover, portfolio, 
                                 max_order_handler, ib_broker, events_queue, 
                                 trading_schedule, trading_end, stat)
#start trading
trading_session.start_trading()
```
