

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 28 12:51:56 2021
@author: ron
"""
import unittest
from datetime import date, time
from tradingsystem.trading_schedule.us_stock_schedule import USStockSchedule
from tradingsystem.calendar.calendar import Calendlar


class MockUSStockSchedule(USStockSchedule):
    """
    since the parent __init__ method calls _config()
    which generates federal holidays and weekends,
    this mock class orverrides the __init__ method
    so that _gen_federal_holidays() and _gen_weekends()
    can be tested individually.
    """
    def __init__(self):
        self.calendar = Calendlar()
        self.close_early_date = set()
        self.summer_start_date = None
        self.winter_start_date = None
        

class TestUSStockSchedule(unittest.TestCase):
    """
    Test if the trading hours and public holidays are generated correctly for a given year.
    The result is compared with holidays listed in https://www.nyse.com/markets/hours-calendars
    """        
    def test_federal_holidays_2023(self):
        stock_schedule = MockUSStockSchedule()
        stock_schedule._gen_federal_holidays(2023)  
        calendar = stock_schedule.calendar
        
        new_year = date(2023, 1, 2)
        martin = date(2023, 1, 16)
        washington = date(2023, 2, 20)
        good_friday = date(2023, 4, 7)
        memorial_day = date(2023, 5, 29)
        juneteenth = date(2023, 6, 19)
        independence = date(2023, 7, 4)
        labor = date(2023, 9, 4)
        thanksgiving = date(2023, 11, 23)
        christams = date(2023, 12, 25)
        
        self.assertTrue(calendar.is_holiday(new_year))
        self.assertTrue(calendar.is_holiday(martin))
        self.assertTrue(calendar.is_holiday(washington))
        self.assertTrue(calendar.is_holiday(good_friday))
        self.assertTrue(calendar.is_holiday(memorial_day))
        self.assertTrue(calendar.is_holiday(juneteenth))
        self.assertTrue(calendar.is_holiday(independence))
        self.assertTrue(calendar.is_holiday(labor))
        self.assertTrue(calendar.is_holiday(thanksgiving))
        self.assertTrue(calendar.is_holiday(christams))

        
    def test_new_years_sat(self):
        """
        if new years is on sat, it should not precede to Friday
        """
        stock_schedule = MockUSStockSchedule()
        stock_schedule._gen_federal_holidays(2022)  
        calendar = stock_schedule.calendar
        new_year = date(2022, 1, 1)      
        self.assertFalse(calendar.is_holiday(new_year))

        
    def test_christmas_sat(self):
        """
        if christmas is on sat, it moves to 24th and the market
        should be closed on that day rather than closed early 
        """
        stock_schedule = MockUSStockSchedule()
        stock_schedule._gen_federal_holidays(2021)   
        calendar = stock_schedule.calendar
        christmas = date(2021, 12, 24)      
        self.assertTrue(calendar.is_holiday(christmas))
        self.assertFalse(christmas in stock_schedule.close_early_date)
        
    
    def test_close_early(self):
        """
        Test if some dates before/after the public holidays
        are regards as dates that the maket closes early
        """
        stock_schedule = MockUSStockSchedule()
        stock_schedule._gen_federal_holidays(2024)
        close_early = stock_schedule.close_early_date
        before_independence = date(2024, 7, 3)  
        after_thanksgiving = date(2024, 11, 29)  
        christams_Eve = date(2024, 12, 24)  
        self.assertTrue(before_independence in close_early)
        self.assertTrue(after_thanksgiving in close_early)
        self.assertTrue(christams_Eve in close_early)
        
    
    def test_daylight_saving_date(self):
        stock_schedule = MockUSStockSchedule()
        stock_schedule.summer_start_date = stock_schedule._find_nth_day(2022, 3, 6, 2)
        stock_schedule.winter_start_date = stock_schedule._find_nth_day(2022, 11, 6, 1)
        summer_time = date(2022, 3, 13)
        winter_time = date(2022, 11, 6)
        self.assertEqual(summer_time, stock_schedule.summer_start_date)
        self.assertEqual(winter_time, stock_schedule.winter_start_date)
    
    
    def test_gen_weekends(self):
        """
        test if all weekends generated correctly for a given year
        """
        stock_schedule = MockUSStockSchedule()
        stock_schedule._gen_weekends(2022)
        calendar = stock_schedule.calendar
        #there are 105 sundays and saturdays in 2022
        self.assertEqual(105, len(calendar.holidays))
        
    
    def test_trading_hours(self):
        stock_schedule = MockUSStockSchedule()
        stock_schedule._gen_federal_holidays(2023)
        stock_schedule._gen_weekends(2023)
        stock_schedule.summer_start_date = stock_schedule._find_nth_day(2023, 3, 6, 2)
        stock_schedule.winter_start_date = stock_schedule._find_nth_day(2023, 11, 6, 1)
                
        normal_summer_hours = stock_schedule.get_trading_hours(date(2023, 3, 15))
        early_summer_hours = stock_schedule.get_trading_hours(date(2023, 7, 3))
        normal_winter_hours = stock_schedule.get_trading_hours(date(2023, 1, 10))
        early_winter_hours = stock_schedule.get_trading_hours(date(2023, 11, 24))
        
        # self.assertEqual(normal_summer_hours, (time(13,30), time(20,00)))
        # self.assertEqual(early_summer_hours, (time(13,30), time(17,00))) 
        # self.assertEqual(normal_winter_hours, (time(14,30), time(21,00))) 
        # self.assertEqual(early_winter_hours, (time(14,30), time(18,00))) 
        self.assertEqual(normal_summer_hours, (1678887000, 1678910400))
        self.assertEqual(early_summer_hours, (1688391000, 1688403600))
        self.assertEqual(normal_winter_hours, (1673361000, 1673384400))
        self.assertEqual(early_winter_hours, (1700836200, 1700848800)) 
        
        

if __name__ == '__main__':
    unittest.main(verbosity=2)  