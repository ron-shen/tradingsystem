from datetime import datetime, time, timezone, timedelta
from Trading_Schedule.base import BaseSchedule

class FXSchedule(BaseSchedule):
    def __init__(self, year=datetime.utcnow().year):
        self._gen_weekends(year)
        

    def get_trading_hours(self, date):
        start = datetime.combine(date, time(00, 00, tzinfo=timezone.utc)).timestamp()
        end = datetime.combine(date + timedelta(days=1), time(00, 00, tzinfo=timezone.utc)).timestamp()
        
        return (start, end)
        





    

