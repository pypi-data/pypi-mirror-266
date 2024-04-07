from datewise.datewise import *
from datetime import datetime
import pytest
import pandas as pd



# identify_date_format

def test1_identify_date_format_datetime_type():

    today = datetime.now()

    assert identify_date_format(today) == "Datetime type, no specific format"


def test2_identify_date_format_pandas_timestamp_type():

    today = pd.Timestamp.now()

    assert identify_date_format(today) == "Pandas Timestamp type, no specific format"


def test3_identify_date_format_unknown_data_type():

    today = 123

    with pytest.raises(ValueError) as exc_info:
        identify_date_format(today)

    assert str(exc_info.value) == "Unknow data type of date variable"


def test4_identify_date_format_unknown_date_format():

    today = '2024-03-1813:00:00'

    assert identify_date_format(today) == False


def test5_identify_date_format_specific_type_no1():

    today = '2024-03-18'

    assert identify_date_format(today) == "%Y-%m-%d"


def test6_identify_date_format_specific_type_no2():

    today = '2024/03/18 15:00:00'

    assert identify_date_format(today) == "%Y/%m/%d %H:%M:%S"


# date_comparison
    
def test_1_date_comparison_two_same_dates():

    date1 = '2024-03-17'
    date2 = '2024-03-17'

    assert date_comparison(date_1=date1, date_2=date2, operation='==') == True


def test_2_date_comparison_different_dates():

    date1 = '2024-03-18'
    date2 = '2024-03-17'

    assert date_comparison(date_1=date1, date_2=date2, operation='>') == True


def test_3_date_comparison_different_dates():

    date1 = '2024-03-18'
    date2 = '2024-03-17'

    assert date_comparison(date_1=date1, date_2=date2, operation='<') == False


def test_4_date_comparison_different_data_types():

    date1 = datetime.now()
    date2 = '2024-03-17'

    assert date_comparison(date_1=date1, date_2=date2, operation='>') == True


def test_5_date_comparison_different_data_types():

    date1 = (datetime.now() - timedelta(days=1))
    date2 = pd.Timestamp.now()

    assert date_comparison(date_1=date1, date_2=date2, operation='<') == True


def test_6_date_comparison_different_data_types():

    date1 = '2024-03-17'
    date2 = (datetime.now() - timedelta(days=1))

    assert date_comparison(date_1=date1, date_2=date2, operation='<') == True


# week_start

def test1_week_start_date_as_string():

    date = '2024-03-19'

    assert week_start(date) == '2024-03-18'


def test2_week_start_date_as_timestamp():

    date = pd.Timestamp('2024-03-19 12:30:00')

    assert week_start(date) == '2024-03-18'


def test3_week_start_date_as_datetime():

    date = datetime(year=2024, month=3, day=19)

    assert week_start(date) == '2024-03-18'


def test4_week_start_unknown_date_type():

    date = 123

    with pytest.raises(ValueError) as exc_info:
        week_start(date)

    assert str(exc_info.value) == "Unknow data type of date variable"


# week_end
    
def test1_week_end_date_as_string_weekend_false():

    date = '2024-03-19'

    assert week_end(date, False) == 'Business Week ends: 2024-03-22' 


def test2_week_end_date_as_timestamp_weekend_false():

    date = pd.Timestamp('2024-03-19 12:30:00')

    assert week_end(date, False) == 'Business Week ends: 2024-03-22' 


def test3_week_end_date_as_datetime_weekend_false():

    date = datetime(year=2024, month=3, day=19)

    assert week_end(date, False) == 'Business Week ends: 2024-03-22' 


def test4_week_end_date_as_string_weekend_true():

    date = '2024-03-19'

    assert week_end(date, True) == 'Full Week ends: 2024-03-24' 


def test5_week_end_date_as_timestamp_weekend_true():

    date = pd.Timestamp('2024-03-19 12:30:00')

    assert week_end(date, True) == 'Full Week ends: 2024-03-24' 


def test6_week_end_date_as_datetime_weekend_true():

    date = datetime(year=2024, month=3, day=19)

    assert week_end(date, True) == 'Full Week ends: 2024-03-24' 


def test7_week_end_date_as_string_weekend_false_end_of_the_week():

    date = '2024-03-22'

    assert week_end(date, False) == 'Today is the end of the business week.'


def test8_week_end_date_as_string_weekend_true_end_of_the_week():

    date = '2024-03-24'

    assert week_end(date, True) == 'Today is the end of the full week.'


def test9_week_end_date_as_string_weekend_true_date_unknown_format():

    date = 'abc'

    with pytest.raises(ValueError) as exc_info:
        week_end(date, True)

    assert str(exc_info.value) == "Couldn't process such date format."


# date_operations
    
def test1_date_operations_date_string_operation_addition_frequency_day_weekend_false():

    date = '2024-03-19'
    range = 5

    assert date_operations(date=date, operation='+', frequency='day', range=range, weekend=False) == 'Added date without weekend: 2024-03-26'


def test2_date_operations_date_timestamp_operation_addition_frequency_day_weekend_false():

    date = pd.Timestamp('2024-03-19 12:30:00')
    range = 5

    assert date_operations(date=date, operation='+', frequency='day', range=range, weekend=False) == 'Added date without weekend: 2024-03-26'


def test3_date_operations_date_datetime_operation_addition_frequency_day_weekend_false():

    date = datetime(year=2024, month=3, day=19)
    range = 9

    assert date_operations(date=date, operation='+', frequency='day', range=range, weekend=False) == 'Added date without weekend: 2024-04-01'


def test4_date_operations_date_string_operation_addition_frequency_month_weekend_false():

    date = '2024-03-19'
    range = 1

    assert date_operations(date=date, operation='+', frequency='month', range=range, weekend=False) == 'Added date: 2024-04-19'


def test5_date_operations_date_timestamp_operation_addition_frequency_month_weekend_false():

    date = pd.Timestamp('2024-03-19 12:30:00')
    range = 2

    assert date_operations(date=date, operation='+', frequency='month', range=range, weekend=False) == 'Added date: 2024-05-19'


def test6_date_operations_date_datetime_operation_addition_frequency_month_weekend_false():

    date = datetime(year=2024, month=3, day=19)
    range = 3

    assert date_operations(date=date, operation='+', frequency='month', range=range, weekend=False) == 'Added date: 2024-06-19'


def test7_date_operations_date_string_operation_addition_frequency_year_weekend_false():

    date = '2024-03-19'
    range = 1

    assert date_operations(date=date, operation='+', frequency='year', range=range, weekend=False) == 'Added date: 2025-03-19'


def test8_date_operations_date_timestamp_operation_addition_frequency_year_weekend_false():

    date = pd.Timestamp('2024-03-19 12:30:00')
    range = 2

    assert date_operations(date=date, operation='+', frequency='year', range=range, weekend=False) == 'Added date: 2026-03-19'


def test9_date_operations_date_datetime_operation_addition_frequency_year_weekend_false():

    date = datetime(year=2024, month=3, day=19)
    range = 3

    assert date_operations(date=date, operation='+', frequency='year', range=range, weekend=False) == 'Added date: 2027-03-19'


def test10_date_operations_date_string_operation_addition_frequency_day_weekend_true():

    date = '2024-03-19'
    range = 5

    assert date_operations(date=date, operation='+', frequency='day', range=range, weekend=True) == 'Added date with weekend: 2024-03-24'


def test11_date_operations_date_timestamp_operation_addition_frequency_day_weekend_true():

    date = pd.Timestamp('2024-03-19 12:30:00')
    range = 5

    assert date_operations(date=date, operation='+', frequency='day', range=range, weekend=True) == 'Added date with weekend: 2024-03-24'


def test12_date_operations_date_datetime_operation_addition_frequency_day_weekend_true():

    date = datetime(year=2024, month=3, day=19)
    range = 9

    assert date_operations(date=date, operation='+', frequency='day', range=range, weekend=True) == 'Added date with weekend: 2024-03-28'


def test13_date_operations_date_string_operation_addition_frequency_month_weekend_true():

    date = '2024-03-19'
    range = 1

    assert date_operations(date=date, operation='+', frequency='month', range=range, weekend=True) == 'Added date: 2024-04-19'


def test14_date_operations_date_timestamp_operation_addition_frequency_month_weekend_true():

    date = pd.Timestamp('2024-03-19 12:30:00')
    range = 2

    assert date_operations(date=date, operation='+', frequency='month', range=range, weekend=True) == 'Added date: 2024-05-19'


def test15_date_operations_date_datetime_operation_addition_frequency_month_weekend_true():

    date = datetime(year=2024, month=3, day=19)
    range = 3

    assert date_operations(date=date, operation='+', frequency='month', range=range, weekend=True) == 'Added date: 2024-06-19'


def test16_date_operations_date_string_operation_addition_frequency_year_weekend_true():

    date = '2024-03-19'
    range = 1

    assert date_operations(date=date, operation='+', frequency='year', range=range, weekend=True) == 'Added date: 2025-03-19'


def test17_date_operations_date_timestamp_operation_addition_frequency_year_weekend_true():

    date = pd.Timestamp('2024-03-19 12:30:00')
    range = 2

    assert date_operations(date=date, operation='+', frequency='year', range=range, weekend=True) == 'Added date: 2026-03-19'


def test18_date_operations_date_datetime_operation_addition_frequency_year_weekend_true():

    date = datetime(year=2024, month=3, day=19)
    range = 3

    assert date_operations(date=date, operation='+', frequency='year', range=range, weekend=True) == 'Added date: 2027-03-19'


def test19_date_operations_date_string_operation_addition_frequency_day_weekend_false():

    date = '2024-03-19'
    range = 5

    assert date_operations(date=date, operation='-', frequency='day', range=range, weekend=False) == 'Subtracted date without weekend: 2024-03-12'


def test20_date_operations_date_timestamp_operation_addition_frequency_day_weekend_false():

    date = pd.Timestamp('2024-03-19 12:30:00')
    range = 5

    assert date_operations(date=date, operation='-', frequency='day', range=range, weekend=False) == 'Subtracted date without weekend: 2024-03-12'


def test21_date_operations_date_datetime_operation_addition_frequency_day_weekend_false():

    date = datetime(year=2024, month=3, day=19)
    range = 9

    assert date_operations(date=date, operation='-', frequency='day', range=range, weekend=False) == 'Subtracted date without weekend: 2024-03-06'


def test22_date_operations_date_string_operation_addition_frequency_month_weekend_false():

    date = '2024-03-19'
    range = 1

    assert date_operations(date=date, operation='-', frequency='month', range=range, weekend=False) == 'Subtracted date: 2024-02-19'


def test23_date_operations_date_timestamp_operation_addition_frequency_month_weekend_false():

    date = pd.Timestamp('2024-03-19 12:30:00')
    range = 2

    assert date_operations(date=date, operation='-', frequency='month', range=range, weekend=False) == 'Subtracted date: 2024-01-19'


def test24_date_operations_date_datetime_operation_addition_frequency_month_weekend_false():

    date = datetime(year=2024, month=3, day=19)
    range = 3

    assert date_operations(date=date, operation='-', frequency='month', range=range, weekend=False) == 'Subtracted date: 2023-12-19'


def test25_date_operations_date_string_operation_addition_frequency_year_weekend_false():

    date = '2024-03-19'
    range = 1

    assert date_operations(date=date, operation='-', frequency='year', range=range, weekend=False) == 'Subtracted date: 2023-03-19'


def test26_date_operations_date_timestamp_operation_addition_frequency_year_weekend_false():

    date = pd.Timestamp('2024-03-19 12:30:00')
    range = 2

    assert date_operations(date=date, operation='-', frequency='year', range=range, weekend=False) == 'Subtracted date: 2022-03-19'


def test27_date_operations_date_datetime_operation_addition_frequency_year_weekend_false():

    date = datetime(year=2024, month=3, day=19)
    range = 3

    assert date_operations(date=date, operation='-', frequency='year', range=range, weekend=False) == 'Subtracted date: 2021-03-19'


def test28_date_operations_date_string_operation_addition_frequency_day_weekend_true():

    date = '2024-03-19'
    range = 5

    assert date_operations(date=date, operation='-', frequency='day', range=range, weekend=True) == 'Subtracted date with weekend: 2024-03-14'


def test29_date_operations_date_timestamp_operation_addition_frequency_day_weekend_true():

    date = pd.Timestamp('2024-03-19 12:30:00')
    range = 5

    assert date_operations(date=date, operation='-', frequency='day', range=range, weekend=True) == 'Subtracted date with weekend: 2024-03-14'


def test30_date_operations_date_datetime_operation_addition_frequency_day_weekend_true():

    date = datetime(year=2024, month=3, day=19)
    range = 9

    assert date_operations(date=date, operation='-', frequency='day', range=range, weekend=True) == 'Subtracted date with weekend: 2024-03-10'


def test31_date_operations_date_string_operation_addition_frequency_month_weekend_true():

    date = '2024-03-19'
    range = 1

    assert date_operations(date=date, operation='-', frequency='month', range=range, weekend=True) == 'Subtracted date: 2024-02-19'


def test32_date_operations_date_timestamp_operation_addition_frequency_month_weekend_true():

    date = pd.Timestamp('2024-03-19 12:30:00')
    range = 2

    assert date_operations(date=date, operation='-', frequency='month', range=range, weekend=True) == 'Subtracted date: 2024-01-19'


def test33_date_operations_date_datetime_operation_addition_frequency_month_weekend_true():

    date = datetime(year=2024, month=3, day=19)
    range = 3

    assert date_operations(date=date, operation='-', frequency='month', range=range, weekend=True) == 'Subtracted date: 2023-12-19'


def test34_date_operations_date_string_operation_addition_frequency_year_weekend_true():

    date = '2024-03-19'
    range = 1

    assert date_operations(date=date, operation='-', frequency='year', range=range, weekend=True) == 'Subtracted date: 2023-03-19'


def test35_date_operations_date_timestamp_operation_addition_frequency_year_weekend_true():

    date = pd.Timestamp('2024-03-19 12:30:00')
    range = 2

    assert date_operations(date=date, operation='-', frequency='year', range=range, weekend=True) == 'Subtracted date: 2022-03-19'


def test36_date_operations_date_datetime_operation_addition_frequency_year_weekend_true():

    date = datetime(year=2024, month=3, day=19)
    range = 3

    assert date_operations(date=date, operation='-', frequency='year', range=range, weekend=True) == 'Subtracted date: 2021-03-19'


# range_calculation
    
def test1_date1_string_date2_string_range_calculation_weekend_false_frequncy_day():

    start = '2024-03-19'
    end = '2024-04-02'

    assert range_calculation(start=start, end=end, weekend=False, frequency='day') == "Days between two dates are: ['2024-04-01', '2024-03-31', '2024-03-30', '2024-03-29', '2024-03-28', '2024-03-27', '2024-03-26', '2024-03-25', '2024-03-24', '2024-03-23', '2024-03-22', '2024-03-21', '2024-03-20']"


def test2_date1_string_date2_timestamp_range_calculation_weekend_false_frequncy_day():

    start = '2024-03-19'
    end =  pd.Timestamp('2024-04-02 12:30:00')

    assert range_calculation(start=start, end=end, weekend=False, frequency='day') == "Days between two dates are: ['2024-04-01', '2024-03-31', '2024-03-30', '2024-03-29', '2024-03-28', '2024-03-27', '2024-03-26', '2024-03-25', '2024-03-24', '2024-03-23', '2024-03-22', '2024-03-21', '2024-03-20']"


def test3_date1_timestamp_date2_datetime_range_calculation_weekend_false_frequncy_day():

    start = pd.Timestamp('2024-03-19 12:30:00')
    end = datetime(year=2024, month=4, day=2)

    assert range_calculation(start=start, end=end, weekend=False, frequency='day') == "Days between two dates are: ['2024-04-01', '2024-03-31', '2024-03-30', '2024-03-29', '2024-03-28', '2024-03-27', '2024-03-26', '2024-03-25', '2024-03-24', '2024-03-23', '2024-03-22', '2024-03-21', '2024-03-20']"


def test4_date1_string_date2_string_range_calculation_weekend_false_frequncy_week():

    start = '2024-03-19'
    end = '2024-04-02'

    assert range_calculation(start=start, end=end, weekend=False, frequency='week') == "Difference between two dates is 1 week(s) and 6 days. If you want to see specific dates, switch to format='day'"


def test5_date1_string_date2_timestamp_range_calculation_weekend_false_frequncy_week():

    start = '2024-03-19'
    end =  pd.Timestamp('2024-04-02 12:30:00')

    assert range_calculation(start=start, end=end, weekend=False, frequency='week') == "Difference between two dates is 1 week(s) and 6 days. If you want to see specific dates, switch to format='day'"


def test6_date1_timestamp_date2_datetime_range_calculation_weekend_false_frequncy_week():

    start = pd.Timestamp('2024-03-19 12:30:00')
    end = datetime(year=2024, month=4, day=2)

    assert range_calculation(start=start, end=end, weekend=False, frequency='week') == "Difference between two dates is 1 week(s) and 6 days. If you want to see specific dates, switch to format='day'"


def test7_date1_string_date2_string_range_calculation_weekend_false_frequncy_month():

    start = '2024-03-19'
    end = '2024-04-02'

    assert range_calculation(start=start, end=end, weekend=False, frequency='month') ==  "Difference between two dates is 0 month(s) and 13 days. If you want to see specific dates, switch to format='day'"


def test8_date1_string_date2_timestamp_range_calculation_weekend_false_frequncy_month():

    start = '2024-03-19'
    end =  pd.Timestamp('2024-04-02 12:30:00')

    assert range_calculation(start=start, end=end, weekend=False, frequency='month') == "Difference between two dates is 0 month(s) and 13 days. If you want to see specific dates, switch to format='day'"


def test9_date1_timestamp_date2_datetime_range_calculation_weekend_false_frequncy_month():

    start = pd.Timestamp('2024-03-19 12:30:00')
    end = datetime(year=2024, month=4, day=2)

    assert range_calculation(start=start, end=end, weekend=False, frequency='month') == "Difference between two dates is 0 month(s) and 13 days. If you want to see specific dates, switch to format='day'"


def test10_date1_string_date2_string_range_calculation_weekend_false_frequncy_quarter():

    start = '2024-03-19'
    end = '2024-04-02'

    assert range_calculation(start=start, end=end, weekend=False, frequency='quarter') == "Difference between two dates is 0 quarter(s) and 13 days. If you want to see specific dates, switch to format='day'"


def test11_date1_string_date2_timestamp_range_calculation_weekend_false_frequncy_quarter():

    start = '2024-03-19'
    end =  pd.Timestamp('2024-04-02 12:30:00')

    assert range_calculation(start=start, end=end, weekend=False, frequency='quarter') == "Difference between two dates is 0 quarter(s) and 13 days. If you want to see specific dates, switch to format='day'"


def test12_date1_timestamp_date2_datetime_range_calculation_weekend_false_frequncy_quarter():

    start = pd.Timestamp('2024-03-19 12:30:00')
    end = datetime(year=2024, month=4, day=2)

    assert range_calculation(start=start, end=end, weekend=False, frequency='quarter') == "Difference between two dates is 0 quarter(s) and 13 days. If you want to see specific dates, switch to format='day'"


def test13_date1_string_date2_string_range_calculation_weekend_false_frequncy_year():

    start = '2024-03-19'
    end = '2024-04-02'

    assert range_calculation(start=start, end=end, weekend=False, frequency='year') == "Difference between two dates is 0 year(s) and 13 days. If you want to see specific dates, switch to format='day'"


def test14_date1_string_date2_timestamp_range_calculation_weekend_false_frequncy_year():

    start = '2024-03-19'
    end =  pd.Timestamp('2024-04-02 12:30:00')

    assert range_calculation(start=start, end=end, weekend=False, frequency='year') == "Difference between two dates is 0 year(s) and 13 days. If you want to see specific dates, switch to format='day'"


def test15_date1_timestamp_date2_datetime_range_calculation_weekend_false_frequncy_year():

    start = pd.Timestamp('2024-03-19 12:30:00')
    end = datetime(year=2024, month=4, day=2)

    assert range_calculation(start=start, end=end, weekend=False, frequency='year') == "Difference between two dates is 0 year(s) and 13 days. If you want to see specific dates, switch to format='day'"


def test16_date1_string_date2_string_range_calculation_weekend_true_frequncy_day():

    start = '2024-03-19'
    end = '2024-04-02'

    assert range_calculation(start=start, end=end, weekend=True, frequency='day') == "Business days between two dates are: ['2024-04-01', '2024-03-29', '2024-03-28', '2024-03-27', '2024-03-26', '2024-03-25', '2024-03-22', '2024-03-21', '2024-03-20']"


def test17_date1_string_date2_timestamp_range_calculation_weekend_true_frequncy_day():

    start = '2024-03-19'
    end =  pd.Timestamp('2024-04-02 12:30:00')

    assert range_calculation(start=start, end=end, weekend=True, frequency='day') == "Business days between two dates are: ['2024-04-01', '2024-03-29', '2024-03-28', '2024-03-27', '2024-03-26', '2024-03-25', '2024-03-22', '2024-03-21', '2024-03-20']"


def test18_date1_timestamp_date2_datetime_range_calculation_weekend_true_frequncy_day():

    start = pd.Timestamp('2024-03-19 12:30:00')
    end = datetime(year=2024, month=4, day=2)

    assert range_calculation(start=start, end=end, weekend=True, frequency='day') == "Business days between two dates are: ['2024-04-01', '2024-03-29', '2024-03-28', '2024-03-27', '2024-03-26', '2024-03-25', '2024-03-22', '2024-03-21', '2024-03-20']"


def test19_date1_string_date2_string_range_calculation_weekend_true_frequncy_week():

    start = '2024-03-19'
    end = '2024-04-02'

    assert range_calculation(start=start, end=end, weekend=True, frequency='week') == "Difference between two dates is 1 week(s) and 4 days. If you want to see specific dates, switch to format='day'"


def test20_date1_string_date2_timestamp_range_calculation_weekend_true_frequncy_week():

    start = '2024-03-19'
    end =  pd.Timestamp('2024-04-02 12:30:00')

    assert range_calculation(start=start, end=end, weekend=True, frequency='week') == "Difference between two dates is 1 week(s) and 4 days. If you want to see specific dates, switch to format='day'"


def test21_date1_timestamp_date2_datetime_range_calculation_weekend_true_frequncy_week():

    start = pd.Timestamp('2024-03-19 12:30:00')
    end = datetime(year=2024, month=4, day=2)

    assert range_calculation(start=start, end=end, weekend=True, frequency='week') == "Difference between two dates is 1 week(s) and 4 days. If you want to see specific dates, switch to format='day'"


def test22_date1_string_date2_string_range_calculation_weekend_true_frequncy_month():

    start = '2024-03-19'
    end = '2024-04-02'

    assert range_calculation(start=start, end=end, weekend=True, frequency='month') ==  "Difference between two dates is 0 month(s) and 9 days. If you want to see specific dates, switch to format='day'"


def test23_date1_string_date2_timestamp_range_calculation_weekend_true_frequncy_month():

    start = '2024-03-19'
    end =  pd.Timestamp('2024-04-02 12:30:00')

    assert range_calculation(start=start, end=end, weekend=True, frequency='month') == "Difference between two dates is 0 month(s) and 9 days. If you want to see specific dates, switch to format='day'"


def test24_date1_timestamp_date2_datetime_range_calculation_weekend_true_frequncy_month():

    start = pd.Timestamp('2024-03-19 12:30:00')
    end = datetime(year=2024, month=4, day=2)

    assert range_calculation(start=start, end=end, weekend=True, frequency='month') == "Difference between two dates is 0 month(s) and 9 days. If you want to see specific dates, switch to format='day'"


def test25_date1_string_date2_string_range_calculation_weekend_true_frequncy_quarter():

    start = '2024-03-19'
    end = '2024-04-02'

    assert range_calculation(start=start, end=end, weekend=True, frequency='quarter') == "Difference between two dates is 0 quarter(s) and 9 days. If you want to see specific dates, switch to format='day'"


def test26_date1_string_date2_timestamp_range_calculation_weekend_true_frequncy_quarter():

    start = '2024-03-19'
    end =  pd.Timestamp('2024-04-02 12:30:00')

    assert range_calculation(start=start, end=end, weekend=True, frequency='quarter') == "Difference between two dates is 0 quarter(s) and 9 days. If you want to see specific dates, switch to format='day'"


def test27_date1_timestamp_date2_datetime_range_calculation_weekend_true_frequncy_quarter():

    start = pd.Timestamp('2024-03-19 12:30:00')
    end = datetime(year=2024, month=4, day=2)

    assert range_calculation(start=start, end=end, weekend=True, frequency='quarter') == "Difference between two dates is 0 quarter(s) and 9 days. If you want to see specific dates, switch to format='day'"


def test28_date1_string_date2_string_range_calculation_weekend_true_frequncy_year():

    start = '2024-03-19'
    end = '2024-04-02'

    assert range_calculation(start=start, end=end, weekend=True, frequency='year') == "Difference between two dates is 0 year(s) and 9 days. If you want to see specific dates, switch to format='day'"


def test29_date1_string_date2_timestamp_range_calculation_weekend_true_frequncy_year():

    start = '2024-03-19'
    end =  pd.Timestamp('2024-04-02 12:30:00')

    assert range_calculation(start=start, end=end, weekend=True, frequency='year') == "Difference between two dates is 0 year(s) and 9 days. If you want to see specific dates, switch to format='day'"


def test30_date1_timestamp_date2_datetime_range_calculation_weekend_true_frequncy_year():

    start = pd.Timestamp('2024-03-19 12:30:00')
    end = datetime(year=2024, month=4, day=2)

    assert range_calculation(start=start, end=end, weekend=True, frequency='year') == "Difference between two dates is 0 year(s) and 9 days. If you want to see specific dates, switch to format='day'"


# date_convert
    
def test1_date_convert_from_str_to_pandas():

    date = '2024-03-19'

    assert date_convert(date=date, desired_type='pandas', format='%Y-%m-%d') == pd.Timestamp('2024-03-19 00:00:00')


def test2_date_convert_from_str_to_datetime():

    date = '2024-03-19'

    assert date_convert(date=date, desired_type='datetime', format='%Y-%m-%d') == datetime(2024, 3, 19, 0, 0)


def test3_date_convert_from_pandas_to_str():

    date = pd.Timestamp('2024-03-19 00:00:00')

    assert date_convert(date=date, desired_type='str', format='%Y-%m-%d') == '2024-03-19'


def test4_date_convert_from_pandas_to_datetime():

    date = pd.Timestamp('2024-03-19 00:00:00')

    assert date_convert(date=date, desired_type='datetime', format='%Y-%m-%d') == datetime(2024, 3, 19, 0, 0)


def test5_date_convert_from_datetime_to_str():

    date = datetime(2024, 3, 19, 0, 0)

    assert date_convert(date=date, desired_type='str', format='%Y-%m-%d') == '2024-03-19'


def test6_date_convert_from_datetime_to_pandas():

    date = datetime(2024, 3, 19, 0, 0)

    assert date_convert(date=date, desired_type='pandas', format='%Y-%m-%d') == pd.Timestamp('2024-03-19 00:00:00')






