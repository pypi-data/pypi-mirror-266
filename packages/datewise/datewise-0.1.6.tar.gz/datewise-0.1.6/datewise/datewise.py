from datetime import datetime, timedelta
from typing import Union
import pandas as pd

def identify_date_format(date: Union[str, datetime, pd._libs.tslibs.timestamps.Timestamp]) -> str:

    """
    Identify date format of input date based on pre-determined widely used formats.

    :param date: The date given by a user to identify it's format 
    :type date: str, datetime, pd._libs.tslibs.timestamps.Timestamp

    :return: Date format, if available, else message about error
    :rtype: str
    """

    formats = [
        "%m/%d/%Y", "%m-%d-%Y",
        "%d/%m/%Y", "%d-%m-%Y",
        "%Y/%m/%d", "%Y-%m-%d",
        "%Y/%m/%d", "%Y-%m-%d",
        "%d/%m/%Y", "%d-%m-%Y",
        "%Y %m %d", "%Y-%m-%d",
        "%m %d %Y", "%m-%d-%Y",
        "%d %m %Y", "%d-%m-%Y",
        "%Y:%m:%d", "%Y-%m-%d",
        "%m:%d:%Y", "%m-%d-%Y",
        "%d:%m:%Y", "%d-%m-%Y",
        "%Y %m %d %H:%M:%S", "%Y-%m-%d %H:%M:%S",
        "%Y %m %d %H:%M", "%Y-%m-%d %H:%M",
        "%Y %m %d %H", "%Y-%m-%d %H",
        "%Y %m %d %I:%M:%S %p", "%Y-%m-%d %I:%M:%S %p",
        "%Y %m %d %I:%M %p", "%Y-%m-%d %I:%M %p",
        "%Y %m %d %I %p", "%Y-%m-%d %I %p",
        "%d/%m/%Y %H:%M:%S", "%d-%m-%Y %H:%M:%S",
        "%d/%m/%Y %H:%M", "%d-%m-%Y %H:%M",
        "%d/%m/%Y %H", "%d-%m-%Y %H",
        "%d/%m/%Y %I:%M:%S %p", "%d-%m-%Y %I:%M:%S %p",
        "%d/%m/%Y %I:%M %p", "%d-%m-%Y %I:%M %p",
        "%d/%m/%Y %I %p", "%d-%m-%Y %I %p",
        "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M",
        "%Y-%m-%d %H", "%Y-%m-%d %H",
        "%Y-%m-%d %I:%M:%S %p", "%Y-%m-%d %I:%M:%S %p",
        "%Y-%m-%d %I:%M %p", "%Y-%m-%d %I:%M %p",
        "%Y-%m-%d %I %p", "%Y-%m-%d %I %p",
        "%Y/%m/%d %H:%M:%S", "%Y-%m-%d %H:%M:%S",
        "%Y/%m/%d %H:%M:%S", "%Y-%m-%d %H:%M:%S",
        "%y-%m-%d %H:%M:%S", "%y/%m/%d %H:%M:%S",
        "%y-%m-%d %H:%M", "%y/%m/%d %H:%M",
        "%y-%m-%d %H", "%y/%m/%d %H",
        "%y-%m-%d %I:%M:%S %p", "%y/%m/%d %I:%M:%S %p",
        "%y-%m-%d %I:%M %p", "%y/%m/%d %I:%M %p",
        "%y-%m-%d %I %p", "%y/%m/%d %I %p",
    ]

    if isinstance(date, str):
        for fmt in formats:
            try:
                datetime.strptime(date, fmt)
                return fmt
            except ValueError:
                pass
        return False
    elif isinstance(date, pd._libs.tslibs.timestamps.Timestamp):
        return "Pandas Timestamp type, no specific format"
    elif isinstance(date, datetime):
        return "Datetime type, no specific format"
    else:
        raise ValueError("Unknow data type of date variable")

 
def date_comparison(date_1= Union[str, datetime, pd._libs.tslibs.timestamps.Timestamp], date_2= Union[str, datetime, pd._libs.tslibs.timestamps.Timestamp], operation=str) -> bool:

    """
    Compare two dates given by a surer based on chosen comparison operator

    :param date1: Date no. 1 given by a user to be compared
    :type date1: str, datetime, pd._libs.tslibs.timestamps.Timestamp

    :param date2: Date no. 2 given by a user to be compared
    :type date2: str, datetime, pd._libs.tslibs.timestamps.Timestamp

    :param operation: Any valid comparison sign in string format
    :type operation: str 
    
    :return: True or False value based on a result
    :rtype: bool

    """

    
    if date_1 and date_2 and operation:

        if isinstance(date_1, str) and isinstance(date_2, str): 

            date1_comparison = datetime.strptime(date_1, identify_date_format(date=date_1)) 
            date2_comparison = datetime.strptime(date_2, identify_date_format(date=date_2)) 

            if operation == "==":

                return date1_comparison == date2_comparison
            
            elif operation == "<":

                return date1_comparison < date2_comparison
            
            elif operation == "<=":

                return date1_comparison <= date2_comparison
            
            elif operation == ">":

                return date1_comparison > date2_comparison
            
            elif operation == ">=":

                return date1_comparison >= date2_comparison
            
        elif isinstance(date_1, (pd._libs.tslibs.timestamps.Timestamp, datetime)) or isinstance(date_2, (pd._libs.tslibs.timestamps.Timestamp, datetime)):

            date_1_type = type(date_1)
            date_2_type = type(date_2)

            if date_1_type != str:

                date_1 = date_convert(date_1, 'str', '%Y-%m-%d')

            elif date_2_type != str:

                date_2 = date_convert(date_2, 'str', '%Y-%m-%d')

            return date_comparison(date_1, date_2, operation)        
        else:
            
            raise ValueError("Provided inputs are uncomperable"  )
    
    else: 

        raise ValueError('Missing variable')


def week_start(date: Union[str, datetime, pd._libs.tslibs.timestamps.Timestamp]) -> str:
 
    """
    Find the start of the specific week based on a given date

    :param date: The date given by a user to identify start of the week that the date is in 
    :type date: str, datetime, pd._libs.tslibs.timestamps.Timestamp

    :return: Date representing start of the week
    :rtype: str
    """

    
    if isinstance(date, str):

        fmt = identify_date_format(date)

        if fmt:

            weekday = datetime.strptime(date, fmt).weekday()

            date_start = (datetime.strptime(date, fmt) - timedelta(days=weekday)).strftime(fmt)

            return date_start
    
    elif isinstance(date, (pd._libs.tslibs.timestamps.Timestamp, datetime)):

        converted_date = date_convert(date, 'str', '%Y-%m-%d')

        return week_start(converted_date)
    
    else:
        raise ValueError("Unknow data type of date variable")
    
    
def week_end(date: Union[str, datetime, pd._libs.tslibs.timestamps.Timestamp], weekend:bool) -> str:

    """
    Find the end of the specific week based on a given date for either week as a whole or business week

    :param date: The date given by a user to identify end of the week that the date is in 
    :type date: str, datetime, pd._libs.tslibs.timestamps.Timestamp

    :param weekend: identifier for including or excluding weekend (standard or business week)
    :type weekend: bool

    :return: Date representing end of the full or business week
    :rtype: str
    """


    if isinstance(date, str):

        fmt = identify_date_format(date)

        if fmt:

            weekday = datetime.strptime(date, fmt).weekday()

            if weekend == False:

                if weekday < 3:   

                    date_week_end = (datetime.strptime(date, fmt) + timedelta(days=4 - weekday)).strftime(fmt)
                    return(f'Business Week ends: {date_week_end}')
                
                elif weekday == 4:

                    return('Today is the end of the business week.') 

                else:

                    return('Businees Week has already ended.')

            elif weekend == True:

                if weekday < 6:   

                    date_week_end = (datetime.strptime(date, fmt) + timedelta(days=6 - weekday)).strftime(fmt)
                    return(f'Full Week ends: {date_week_end}')

                else:

                    return('Today is the end of the full week.')
                
        else:

            raise ValueError("Couldn't process such date format.")
    
    elif isinstance(date, (pd._libs.tslibs.timestamps.Timestamp, datetime)):

        converted_date = date_convert(date, 'str', '%Y-%m-%d')

        return week_end(converted_date, weekend)
    
    else:

        raise ValueError("Unknow data type of date variable")


def date_operations(date: Union[str, datetime, pd._libs.tslibs.timestamps.Timestamp], operation:str, frequency:str, range:int, weekend:bool) -> str:

    """
    Adding or subtracting date for chosen frequency in specific range for either standard or business week

    :param date: date from which subtraction or addition will be calculated
    :type date: str, datetime, pd._libs.tslibs.timestamps.Timestamp

    :param operation: subtraction or addition
    :type operation: str

    :param frequency: type of periodicity --> day/month/year
    :type frequency: str

    :param range: number of days/months/year to be added/subtracted to/from a date
    :type range: int

    :param weekend: identifier for including or excluding weekend (standard or business week)
    :type weekend: bool

    :return: New day after subtraction or addition
    :rtype: str
    """


    if date and operation and frequency and range:

        if isinstance(date, str):

            fmt = identify_date_format(date)

            weekday = datetime.strptime(date, fmt).weekday()

            date = datetime.strptime(date, fmt)

            if frequency == 'day':

                if weekend == False:

                    if operation == '+' : 

                        while range: 

                            if range and weekday <= 3 or weekday >= 6:

                                date += timedelta(days=1)
                                weekday = date.weekday()
                                range -= 1                            
                            else:
                                
                                date += timedelta(days=1)
                                weekday = date.weekday()

                        return(f'Added date without weekend: {date.strftime(fmt)}')
                        
                    elif operation == '-':

                        while range: 

                            if range and weekday <= 5 and weekday >= 1:

                                date -= timedelta(days=1)
                                weekday = date.weekday()
                                range -= 1                            
                            else:
                                
                                date -= timedelta(days=1)
                                weekday = date.weekday()

                        return(f'Subtracted date without weekend: {date.strftime(fmt)}')

                elif weekend == True:

                    if operation == '+' : 

                        while range: 

                            date += timedelta(days=1)
                            range -= 1

                        return(f'Added date with weekend: {date.strftime(fmt)}')
                        
                    elif operation == '-':

                        while range:

                            date -= timedelta(days=1)
                            range -= 1
                            
                        return(f'Subtracted date with weekend: {date.strftime(fmt)}')
            
            elif frequency == 'month':

                year = int(date.year)
                month = int(date.month)
                day = int(date.day)

                if operation == '+':

                    month += range

                    while month > 12:

                        month -= 12
                        year += 1

                    date = datetime(year=year, month=month, day=day)

                    return(f'Added date: {date.strftime(fmt)}') 
                
                elif operation == '-':

                    month -= range

                    while month <= 0:

                        month += 12
                        year -= 1
                        
                    date = datetime(year=year, month=month, day=day)

                    return(f'Subtracted date: {date.strftime(fmt)}')
                
            elif frequency == 'year':

                year = int(date.year)
                month = int(date.month)
                day = int(date.day)

                if operation == '+':

                    year += range
                    
                    date = datetime(year=year, month=month, day=day)

                    return(f'Added date: {date.strftime(fmt)}')
                
                elif operation == '-':

                    year -= range
                    
                    date = datetime(year=year, month=month, day=day)

                    return(f'Subtracted date: {date.strftime(fmt)}')  

        elif isinstance(date, (pd._libs.tslibs.timestamps.Timestamp, datetime)):

            converted_date = date_convert(date, 'str', '%Y-%m-%d')

            return date_operations(converted_date, operation, frequency, range, weekend)
        
        else:
            raise ValueError("Unknow data type of date variable")   
    else: 
        raise ValueError('Missing mandatory variable.')               


def range_calculation(start: Union[str, datetime, pd._libs.tslibs.timestamps.Timestamp], end: Union[str, datetime, pd._libs.tslibs.timestamps.Timestamp], weekend:bool, frequency:str) -> list:

    """
    Calculate range between two dates for standard or business week in different frquencies
    
    :param start: start of the period
    :type start: str, datetime, pd._libs.tslibs.timestamps.Timestamp

    :param end: end of the period
    :type end: str, datetime, pd._libs.tslibs.timestamps.Timestamp

    :param weekend: identifier for including or excluding weekend (standard or business week)
    :type weekend: bool

    :param frequency: type of periodicity --> day/month/year
    :type frequency: str

    :return: Range of days/months/year between two given dates
    :rtype: list
    """


    if start and end and frequency and range: 

        if isinstance(start, str) and isinstance(end, str): 

            if date_comparison(end, start, '>'):
                max_date = end
                min_date = start
            else:
                max_date = start
                min_date = end

            max_format = identify_date_format(start)
            max_date = datetime.strptime(end, max_format)

            min_format = identify_date_format(end)
            min_date = datetime.strptime(start, min_format)

            days_between = []

            if weekend:

                while max_date != min_date + timedelta(days=1):

                    max_date -= timedelta(days=1)
                    if max_date.weekday() < 5:
                        days_between.append(max_date.strftime(max_format))
                    else:
                        pass

                output =  f'Business days between two dates are: {days_between}'                

            else:

                while max_date != min_date + timedelta(days=1):

                    max_date -= timedelta(days=1)
                    days_between.append(max_date.strftime(max_format))
                
                output = f'Days between two dates are: {days_between}'

            if frequency == 'day':

                return output
            
            elif frequency == 'week':

                week_difference = len(days_between) / 7

                if type(week_difference) != int:

                    if weekend:
                        
                        weeks = int(week_difference)
                        days = len(days_between) % 5

                    else:

                        weeks = int(week_difference)
                        days = len(days_between) % 7

                return f"Difference between two dates is {weeks} week(s) and {days} days. If you want to see specific dates, switch to format='day'"

            elif frequency == 'month':

                month_difference = len(days_between) / 30

                if type(month_difference) != int:

                    months = int(month_difference)
                    days = len(days_between) % 30

                return f"Difference between two dates is {months} month(s) and {days} days. If you want to see specific dates, switch to format='day'"
            
            elif frequency == 'quarter':

                quarter_difference = len(days_between) / 90

                if type(quarter_difference) != int:

                    quarters = int(quarter_difference)
                    days = len(days_between) % 90

                return f"Difference between two dates is {quarters} quarter(s) and {days} days. If you want to see specific dates, switch to format='day'"
            
            elif frequency == 'year':

                year_difference = len(days_between) / 365

                if type(year_difference) != int:

                    years = int(year_difference)
                    days = len(days_between) % 365

                return f"Difference between two dates is {years} year(s) and {days} days. If you want to see specific dates, switch to format='day'"
        
        elif isinstance(start, (pd._libs.tslibs.timestamps.Timestamp, datetime)) or isinstance(end, (pd._libs.tslibs.timestamps.Timestamp, datetime)):

            start_type = type(start)
            end_type = type(end)

            if start_type != str and end_type != str:

                start = date_convert(start, 'str', '%Y-%m-%d')
                end = date_convert(end, 'str', '%Y-%m-%d')
            
            elif start_type != str and end_type == str:

                start = date_convert(start, 'str', '%Y-%m-%d')

            elif end_type != str and start_type == str:

                end = date_convert(end, 'str', '%Y-%m-%d')

            return range_calculation(start, end, weekend, frequency)
        
        else:
            
            raise ValueError( "Unknow data type of date variable")  
    else:

        raise ValueError('Missing mandatory variable')


def date_convert(date: Union[str, datetime, pd._libs.tslibs.timestamps.Timestamp], desired_type:str, format:str):

    """
    Date conversion based on specified format according do tright party library options

    :param date: date for conversion 
    :type date: str, datetime, pd._libs.tslibs.timestamps.Timestamp

    :param desired_type: desired conversion format
    :type desired_type: str

    :param format: valid date format to be new date converted into
    :type format: str

    :return: Converted date
    :rtype: str, datetime, pd._libs.tslibs.timestamps.Timestamp
    """
    

    date_type = str(type(date)).split("'")[1]

    conversions = {
        'pandas._libs.tslibs.timestamps.Timestamp'  : 'pandas', 
        'datetime.datetime'                         : 'datetime', 
        'str'                                       : 'str'
    }

    desired_result = conversions[date_type] + '-' + desired_type

    conversions = {
        'str-pandas'                 : pd.to_datetime(date) if isinstance(date, str) else None, 
        'str-datetime'               : datetime.strptime(date, format) if isinstance(date, str) else None,
        'pandas-str'                 : date.strftime(format) if isinstance(date, pd._libs.tslibs.timestamps.Timestamp) else None,
        'pandas-datetime'            : date.to_pydatetime(date) if isinstance(date, pd._libs.tslibs.timestamps.Timestamp) else None,
        'datetime-str'               : date.strftime(format) if isinstance(date, datetime) else None,
        'datetime-pandas'            : pd.Timestamp(date) if isinstance(date, datetime) else None
    }

    if date_type == desired_type:
        return 'Your date is in desired format'
    
    elif isinstance(date, (pd._libs.tslibs.timestamps.Timestamp, datetime, str)):
        return conversions[desired_result]
    
    else:
        raise ValueError("Unknow data type of date variable")  
