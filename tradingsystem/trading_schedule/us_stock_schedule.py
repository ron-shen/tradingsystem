from datetime import datetime, date, timedelta, time, timezone
import calendar
from .base import BaseSchedule

class USStockSchedule(BaseSchedule):
    def __init__(self, year=datetime.utcnow().year):
        super().__init__()
        self.close_early_date = set()
        self.summer_start_date = None
        self.winter_start_date = None
        self._config(year)


    def get_trading_hours(self, date):
        #Date: a date object
        #winter trading time: 1430 - 2100
        #summer trading time: 1330 - 2000
        #day before independence day 1330 - 1700
        #black friday 1430 - 1800
        #christmas eve 1430 - 1800
        #return timestamp are in UTC
        is_summer_time = self.summer_start_date <= date < self.winter_start_date
        
        if is_summer_time:
            start = datetime.combine(date, time(13, 30, tzinfo=timezone.utc)).timestamp()
            if date in self.close_early_date:
                end = datetime.combine(date, time(17, 00, tzinfo=timezone.utc)).timestamp()
            else:
                end = datetime.combine(date, time(20, 00, tzinfo=timezone.utc)).timestamp()
            return (int(start), int(end))
        #winter time   
        else:
            start = datetime.combine(date, time(14, 30, tzinfo=timezone.utc)).timestamp()
            if date in self.close_early_date:
                end = datetime.combine(date, time(18, 00, tzinfo=timezone.utc)).timestamp()
            else:
                end = datetime.combine(date, time(21, 00, tzinfo=timezone.utc)).timestamp()
            return (int(start), int(end))

  
    def _config(self, year):
        #Winter time begins on the first Sunday of Nov
        #Summer time begins on the second Sunday of Mar
        self.winter_start_date = self._find_nth_day(year, 11, 6, 1)
        self.summer_start_date = self._find_nth_day(year, 3, 6, 2)
        self._gen_federal_holidays(year)
        self._gen_weekends(year)
        

    def _gen_federal_holidays(self, year):
        #generate holidays of current year
        #and days with market closed early
        #and start date of summer and winter time 

        #New Year's Day (possibly moved to Monday if on Sunday)
        #If it is on Saturday, it will not precede to Friday (NYSE Rule 7.2)
        holiday = date(year, 1, 1)
        if holiday.isoweekday() == 7:
            holiday += timedelta(days=1)            
        if holiday.isoweekday() != 6:
            self.calendar.add_holiday(holiday)

        #Martin Luther King's birthday (third Monday in January)
        holiday = self._find_nth_day(year, 1, 0, 3)
        self.calendar.add_holiday(holiday)

        #Washington's birthday (third Monday in February)
        holiday = self._find_nth_day(year, 2, 0, 3)
        self.calendar.add_holiday(holiday)

        #Good Friday (Friday before easter)
        holiday = self._calc_easter(year)
        while holiday.isoweekday() != 5:
             holiday -= timedelta(days=1)
        self.calendar.add_holiday(holiday)

        #Memorial Day (last Monday in May)
        total_monday = len([1 for i in calendar.monthcalendar(year, 5) if i[0] != 0])
        holiday = self._find_nth_day(year, 5, 0, total_monday)
        self.calendar.add_holiday(holiday)

        #Juneteenth (Monday if Sunday or Friday if Saturday)
        holiday = date(year, 6, 19)
        if holiday.isoweekday() == 7:
            holiday += timedelta(days=1)
        elif holiday.isoweekday() == 6:
            holiday -= timedelta(days=1)
        self.calendar.add_holiday(holiday)

        #Independence Day (Monday if Sunday or Friday if Saturday)
        #market is closed early on the day before Independence Day 
        holiday = date(year, 7, 4)
        if holiday.isoweekday() == 7:
            holiday += timedelta(days=1)
        elif holiday.isoweekday() == 6:
            holiday -= timedelta(days=1)
        self.calendar.add_holiday(holiday)       
        if 2 <= holiday.isoweekday() <= 5:      
            date_close_early = holiday - timedelta(days=1)
            self.close_early_date.add(date_close_early)

        #Labor Day (first Monday in September)
        holiday = self._find_nth_day(year, 9, 0, 1)
        self.calendar.add_holiday(holiday)

        #Thanksgiving Day (fourth Thursday in November)
        #market is closed early on the day after Thanksgiving
        holiday = self._find_nth_day(year, 11, 3, 4)
        date_close_early = holiday + timedelta(days=1)
        self.close_early_date.add(date_close_early)
        self.calendar.add_holiday(holiday)

        #Christmas (Monday if Sunday or Friday if Saturday)
        #if Christams is on 12/24, the market should be closed on that day rather than closed early 
        holiday = date(year, 12, 25)
        date_close_early = holiday - timedelta(days=1)
        #market is not closed early if Christams is on Mon, Sat, or Sun
        if 2 <= holiday.isoweekday() <= 5:
            self.close_early_date.add(date_close_early)
        if holiday.isoweekday() == 7:
            holiday += timedelta(days=1)
        elif holiday.isoweekday() == 6:
            holiday -= timedelta(days=1)
        self.calendar.add_holiday(holiday)

                   
    def _find_nth_day(self, year, month, day, nth):
        #day: Monday = 0 to Sunday = 6
        if date(year, month, 1).weekday() == day:
            nth -= 1        
        return calendar.Calendar(day).monthdatescalendar(year, month)[nth][0]


    def _calc_easter(self, year):
        #Use Butcher's Algorithm to calculate Easter
        a = year % 19
        b = year // 100
        c = year % 100
        d = (19 * a + b - b // 4 - ((b - (b + 8) // 25 + 1) // 3) + 15) % 30
        e = (32 + 2 * (b % 4) + 2 * (c // 4) - d - (c % 4)) % 7
        f = d + e - 7 * ((a + 11 * d + 22 * e) // 451) + 114
        month = f // 31
        day = f % 31 + 1    
        return date(year, month, day)



    

