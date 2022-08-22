from abc import ABC, abstractmethod
from ..calendar.calendar import Calendlar
from datetime import date, timedelta


class BaseSchedule(ABC):
    def __init__(self):
        self.calendar = Calendlar()
 
    @abstractmethod
    def get_trading_hours(self, date):
        pass   
   
    def _gen_weekends(self, year):
        d = date(year, 1, 1)
        while d != date(year + 1, 1, 1):
            if 6 <= d.isoweekday() <= 7:
                self.calendar.add_holiday(d)
            d += timedelta(days=1)
            
    
            
      