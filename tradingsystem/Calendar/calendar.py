class Calendlar:
    def __init__(self):
        self.holidays = set()

    def add_holiday(self, date):
        #date: a date object
        self.holidays.add(date)

    def remove_holiday(self, date):
        #date: a date object
        self.holidays.remove(date)

    def is_holiday(self, date):
        #date: a date object
        return date in self.holidays

    def is_weekday(self, date):
        #date: a date object
        return date not in self.holidays
