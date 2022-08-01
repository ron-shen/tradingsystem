from datetime import datetime, time, timezone, timedelta, date
from Trading_Schedule.base import BaseSchedule

class FXSchedule(BaseSchedule):
    def __init__(self, year=datetime.utcnow().year):
        super().__init__()
        self._gen_weekends(year)
        

    def get_trading_hours(self, date):
        start = datetime.combine(date, time(1, 00, tzinfo=timezone.utc)).timestamp()
        end = datetime.combine(date + timedelta(days=1), time(21, 00, tzinfo=timezone.utc)).timestamp()      
        return (start, end)
    
    
    def _gen_weekends(self, year):
        d = date(year, 1, 1)
        while d != date(year + 1, 1, 1):
            if 5 <= d.isoweekday() <= 6:
                self.calendar.add_holiday(d)
            d += timedelta(days=1)
        
        





    

