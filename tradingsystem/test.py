from Trading_Schedule.fx_schedule import FXSchedule
from Trading_Schedule.us_stock_schedule import USStockSchedule
import time
from datetime import datetime, timezone, date, timedelta

class TradingSession:
    """
    Enscapsulates the settings and components for
    carrying out a live trading session through Interactive Brokers.
    """    
    def __init__(self):
        self.trading_end = datetime(2022,7,30,20,0, tzinfo=timezone.utc).timestamp()
        self.trading_schedule = FXSchedule(2022)

             
    def run_session(self):
        """
        Carries out an infinite while loop that polls the
        events queue and directs each event to either the
        strategy component of the execution handler. The
        loop continue until the event queue has been
        emptied.
        """
        while time.time() <= self.trading_end:
            today = date.today()
            # today = date(2022, 7, 31)
            
            if not self.trading_schedule.calendar.is_holiday(today):
                start, end = self.trading_schedule.get_trading_hours(today)
                cur_time = time.time()
                if cur_time < start:
                    sleep_time = start - cur_time
                    print(sleep_time)
                    time.sleep(sleep_time)
                while start <= time.time() <= end:
                    print("test")
                    #go trade
            #reset...
            self._sleep_next_open_day(today)
            # if self.trading_schedule.calendar.is_holiday(today):
            # #market is open               
            # else:
            #     start, end = self.trading_schedule.get_trading_hours(today)
            #     cur_time = time.time()
            #     if cur_time < start:
            #         sleep_time = start - cur_time
            #         print(sleep_time)
            #         time.sleep(sleep_time)
            #     while start <= time.time() <= end:
            #         print("test")
            #         #go trade
                    
        
    def _sleep_next_open_day(self, today):
        next_day = today + timedelta(days=1)
        next_start, _ = self.trading_schedule.get_trading_hours(next_day)
        cur_time = time.time()
        sleep_time = next_start - cur_time
        print(sleep_time)
        time.sleep(sleep_time)
            
                    
                    
a = TradingSession()
a.run_session()