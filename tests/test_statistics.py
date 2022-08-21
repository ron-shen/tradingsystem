#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 26 20:06:59 2021

@author: ron
"""
import unittest
from tradingsystem.statistics.statistics import Statistics
from datetime import datetime, timedelta

class TestStatistics(unittest.TestCase):
    """
    Testing if drawdown and reutrn are correct
    """        
    def test_update(self):
        stat = Statistics(10000)
        date = datetime(2021, 1, 1)
        stat.update(date, 10000)

        date += timedelta(days=1)
        stat.update(date, 10000)

        date += timedelta(days=1)
        stat.update(date, 12000)

        date += timedelta(days=1)
        stat.update(date, 11000)

        date += timedelta(days=1)
        stat.update(date, 15000)

        date += timedelta(days=1)
        stat.update(date, 9000)

        date += timedelta(days=1)
        stat.update(date, 9000)

        date += timedelta(days=1)
        stat.update(date, 10500)

        result = stat.get_results()
        self.assertEqual(result["return"], 5)
        self.assertEqual(result["max_drawdown"], -0.4)
        self.assertEqual(round(result["sharpe_ratio"], 3), 2.29)          



if __name__ == '__main__':
    unittest.main(verbosity=2)