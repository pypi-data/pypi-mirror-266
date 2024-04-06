#  Copyright (c) 2023. ISTMO Center S.A.  All Rights Reserved
#

import calendar
import datetime
import sys
import time
from typing import Union

import dateutil
import numpy as np
import pandas as pd

from dateutil.relativedelta import relativedelta
from .log_utils import Logger

logger = Logger(log_dir='./logs/', logger_name=__name__, log_file=f'{__name__}.log')


def convert_to_datetime(value):
    """
    This function attempts to convert a value to datetime format.
    The function supports multiple datetime string formats including 'YYYY-MM-DD', 'YYYY-MM-DD HH:MM:SS' and 'YYYY-MM-DDTHH:MM:SSZ'.
    """
    formats = ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%SZ']

    for fmt in formats:
        try:
            return datetime.datetime.strptime(value, fmt)
        except ValueError:
            continue
    raise ValueError(f'{value} is not in a supported datetime format')


def get_month_day_range(date) -> tuple[datetime.date, datetime.date]:
    """
    For a date 'date' returns the start and end date for the month of 'date'.

    Month with 31 days:
    date = datetime.date(2011, 7, 27)
    get_month_day_range(date)
    (datetime.date(2011, 7, 1), datetime.date(2011, 7, 31))

    Month with 28 days:
    date = datetime.date(2011, 2, 15)
    get_month_day_range(date)
    (datetime.date(2011, 2, 1), datetime.date(2011, 2, 28))
    """
    if isinstance(date, str):
        date = datetime.datetime.strptime(date, "%Y-%m-%d")
    # date = convert_to_datetime(date)
    first_day: datetime.date = date.replace(day=1)
    last_day: datetime.date = date.replace(day=calendar.monthrange(date.year, date.month)[1])
    return first_day, last_day


def get_date_range(year, month):
    start_date = f"{year}-{month:02d}-01"
    end_date = pd.Period(start_date, freq='M').end_time.strftime('%Y-%m-%d')
    return [start_date, end_date]


def get_quarter(date: datetime) -> datetime:
    """
        Returns the quarter number for a given date.
    """
    return (date.month - 1) // 3 + 1


def get_first_day_of_the_quarter(date: datetime) -> datetime:
    """
    This function returns the first day of the quarter for a given date.

    :param date: A datetime object representing a date
    :type date: datetime.datetime
    :return: A datetime object representing the first day of the quarter
    :rtype: datetime.datetime
    """
    if isinstance(date, str):
        date = datetime.datetime.strptime(date, "%Y-%m-%d")
    return datetime.datetime(date.year, 3 * ((date.month - 1) // 3) + 1, 1)


def get_last_day_of_the_quarter(date: datetime) -> datetime:
    """
        This function returns the last day of the quarter for a given date.

        :param date: A datetime object representing a date
        :type date: datetime.datetime
        :return: A datetime object representing the last day of the quarter
        :rtype: datetime.datetime
    """
    if isinstance(date, str):
        date = datetime.datetime.strptime(date, "%Y-%m-%d")
    quarter = get_quarter(date)
    return datetime.datetime(date.year + 3 * quarter // 12, 3 * quarter % 12 + 1, 1) + datetime.timedelta(days=-1)


def get_quarter_date_range(year, quarter):
    quarter_start_month = (quarter - 1) * 3 + 1
    quarter_start = datetime.datetime(year, quarter_start_month, 1)
    quarter_end = quarter_start + datetime.timedelta(days=90)
    return quarter_start, quarter_end


def get_quarter_timerange(date):
    """
    Returns the start and end dates of a quarter for a given year and quarter number.
    """
    if isinstance(date, str):
        date = datetime.datetime.strptime(date, "%Y-%m-%d")
    start = get_day_starttime(get_first_day_of_the_quarter(date))
    end = get_day_endtime(get_last_day_of_the_quarter(date))
    return start, end


def get_day_timerange(date):
    """
        Returns the start and end times of a given date.
    """
    if isinstance(date, str):
        date = datetime.datetime.strptime(date, "%Y-%m-%d")
    start = datetime.datetime.combine(date, datetime.time.min)
    end = datetime.datetime.combine(date, datetime.time.max)
    return start, end


def get_day_starttime(date):
    if isinstance(date, str):
        date = datetime.datetime.strptime(date, "%Y-%m-%d")
    return datetime.datetime.combine(date, datetime.time.min)


def get_day_endtime(date):
    if isinstance(date, str):
        date = datetime.datetime.strptime(date, "%Y-%m-%d")
    return datetime.datetime.combine(date, datetime.time.max)


def remove_tz_from_datefield(df, date_fields):
    for date_field in date_fields:
        df[date_field] = pd.to_datetime(df[date_field], errors='coerce')
        df[date_field].fillna(pd.to_datetime(datetime.datetime.today(), format='%Y-%m-%d'), inplace=True)
        df[date_field] = df[date_field].apply(
            lambda a: datetime.datetime.strftime(a, "%Y-%m-%d %H:%M:%S"))
        df[date_field] = pd.to_datetime(df[date_field])
    return df


def calc_week_range(date):
    if isinstance(date, str):
        date = datetime.datetime.strptime(date, "%Y-%m-%d")
    current_weekday = date.weekday()
    monday = date - datetime.timedelta(days=current_weekday)
    sunday = monday + datetime.timedelta(days=6)
    return monday, sunday


def get_current_month_period():
    start, end = get_month_day_range(datetime.datetime.today())
    start = get_day_starttime(start)
    end = get_day_endtime(end)
    return start, end


def get_year_timerange(year):
    year_start = datetime.datetime.combine(
        datetime.datetime(year, 1, 1), datetime.time.min)
    year_end = datetime.datetime.combine(datetime.datetime(year, 12, 31), datetime.time.max)
    return year_start, year_end


def get_period_as_dict(start, end):
    return {
        'start': start,
        'end': end,
    }


def is_datetime_column(df, col):
    is_dt_column = False
    unique_values = df[col].unique()
    num_unique = len(unique_values)
    converted = pd.to_datetime(unique_values, errors='coerce', infer_datetime_format=True)
    num_converted = (~converted.isna()).sum()
    if num_converted / num_unique >= 0.5:
        is_dt_column = True
    return is_dt_column


def cast_col_as_datetime(df):
    for col in df.columns:
        if df[col].dtype == object:
            is_dt = is_datetime_column(df, col)
            if is_dt:
                date_format = '%Y-%m-%d %H:%M:%S'
                infer_dt = True
                if len(df[df[col].astype(str).str.contains(":") > 0]) == 0:
                    date_format = '%Y-%m-%d'
                    infer_dt = False
                df[col] = pd.to_datetime(df[col], format=date_format, errors='coerce', infer_datetime_format=infer_dt)
                df[col].fillna(method='ffill', inplace=True)
    return df


class BusinessDays:

    def __init__(self, holiday_list):
        """
            Initialize a BusinessDays object with a given holiday list.
        """
        self.HOLIDAY_LIST = holiday_list
        bd_holidays = [day for year in self.HOLIDAY_LIST for day in self.HOLIDAY_LIST[year]]
        self.bd_cal = np.busdaycalendar(holidays=bd_holidays, weekmask='1111100')

    def get_business_days_count(self, begin_date, end_date):
        """
        Calculate the number of business days between two dates.
        """
        # Validate input dates and convert to datetime objects
        if pd.isna(begin_date) or pd.isna(end_date):
            return np.nan
        if isinstance(begin_date, str):
            try:
                begin_date = datetime.datetime.strptime(begin_date, '%Y-%m-%d')
            except ValueError:
                raise ValueError('begin_date must be a string in the format YYYY-MM-DD')
        elif not isinstance(begin_date, datetime.datetime):
            raise TypeError('begin_date must be a string or datetime.datetime object')

        if isinstance(end_date, str):
            try:
                end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                raise ValueError('end_date must be a string in the format YYYY-MM-DD')
        elif not isinstance(end_date, datetime.datetime):
            raise TypeError('end_date must be a string or datetime.datetime object')

        # try:
        #    begin_date = datetime.datetime.strptime(begin_date, '%Y-%m-%d')
        #    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
        # except ValueError:
        #    raise ValueError('Dates should be strings in the format YYYY-MM-DD')

        # Validate that years are in the holiday list
        years = [str(year) for year in range(begin_date.year, end_date.year + 1)]
        if not all(year in self.HOLIDAY_LIST for year in years):
            raise ValueError('Not all years in date range are in the holiday list')

        return np.busday_count(begin_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), busdaycal=self.bd_cal)

    def calc_business_days_from_df(self, df, begin_date_col, end_date_col, result_col='business_days'):
        # Validate column names
        if not all(col in df.columns for col in [begin_date_col, end_date_col]):
            raise ValueError('Column names not found in DataFrame')
        if df.empty:
            # DataFrame is empty. Cannot perform operation.
            return
        # Ensure dates are in string format
        df[begin_date_col] = pd.to_datetime(df[begin_date_col]).dt.strftime('%Y-%m-%d')
        df[end_date_col] = pd.to_datetime(df[end_date_col]).dt.strftime('%Y-%m-%d')

        # Vectorize np.busday_count function
        v_func = np.vectorize(np.busday_count, excluded=['busdaycal'])

        # Apply vectorized function to DataFrame
        df[result_col] = v_func(df[begin_date_col], df[end_date_col], busdaycal=self.bd_cal)

    def add_business_days(self, start_date, n_days):
        """
        Add n_days business days to start_date.
        """
        # Validate input dates and convert to datetime objects
        try:
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        except ValueError:
            raise ValueError('Date should be a string in the format YYYY-MM-DD')

        # Validate that year is in the holiday list
        if str(start_date.year) not in self.HOLIDAY_LIST:
            logger.warning(f'Year {start_date.year} is not in the holiday list')

        return np.busday_offset(start_date.strftime('%Y-%m-%d'), n_days, roll='forward', busdaycal=self.bd_cal)

    def calc_sla_end_date(self, df, start_date_col, n_days_col, result_col='sla_end_date'):
        """
        Calculate SLA end date based on start date and number of SLA days.
        """
        # Validate column names
        if not all(col in df.columns for col in [start_date_col, n_days_col]):
            raise ValueError('Column names not found in DataFrame')
        if df.empty:
            # DataFrame is empty. Cannot perform operation.
            return
        # Ensure dates are in string format
        df[start_date_col] = pd.to_datetime(df[start_date_col]).dt.strftime('%Y-%m-%d')

        # Vectorize np.busday_offset function
        v_func = np.vectorize(self.add_business_days, excluded=['busdaycal'])

        # Apply vectorized function to DataFrame
        df[result_col] = v_func(df[start_date_col], df[n_days_col])


def get_today():
    return get_today_timerange()


def get_yesterday():
    return get_period_as_dict(get_day_starttime(datetime.datetime.today() - datetime.timedelta(days=1)),
                              get_day_endtime(datetime.datetime.today() - datetime.timedelta(days=1)))


def get_current_month():
    start, end = get_current_month_period()
    return get_period_as_dict(start, end)


def get_previous_month():
    start, end = get_month_day_range(datetime.datetime.today() - relativedelta(months=1))
    start = get_day_starttime(start)
    end = get_day_endtime(end)
    return get_period_as_dict(start, end)


def get_current_year():
    start, end = get_year_timerange(datetime.datetime.today().year)
    return get_period_as_dict(start, end)


def get_today_timerange():
    return get_period_as_dict(get_day_starttime(datetime.datetime.today()),
                              get_day_endtime(datetime.datetime.today()))


def get_current_quarter():
    start, end = get_quarter_timerange(datetime.datetime.today())
    return get_period_as_dict(start, end)


def get_quarter_period(year, quarter):
    start, end = get_quarter_date_range(year, quarter)
    return get_period_as_dict(start, end)


def get_year_period(year):
    start, end = get_year_timerange(year)
    return get_period_as_dict(start, end)


def get_week_range():
    start, end = calc_week_range(datetime.datetime.today())
    return get_period_as_dict(start, end)


def get_last_week():
    start, end = calc_week_range(datetime.datetime.today() - datetime.timedelta(days=7))
    return get_period_as_dict(start, end)


def count_down(msg, maximum):
    for i in range(maximum, 0, -1):
        pad_str = ' ' * len('%d' % 1)
        sys.stdout.write('%s for the next %d seconds %s\r' %
                         (msg, i, pad_str), )
        sys.stdout.flush()
        time.sleep(1)


def load_period(**kwargs):
    start = kwargs.get('start')
    end = kwargs.get('end')
    return get_period_as_dict(start, end)


def load_timeframe(timeframe_func, **kwargs):
    return load_period(**timeframe_func(**kwargs))


def load_current_week():
    return load_timeframe(get_week_range)


def load_current_month():
    return load_timeframe(get_current_month)


def load_current_quarter():
    return load_timeframe(get_current_quarter)


def calc_exact_age(start_date, end_date):
    """
    Calculate the exact age in years, months and days between two dates.
    It returns multiple values: years, months, days.
    """
    if pd.isna(start_date):
        return 0, 0, 0
    if pd.isna(end_date):
        end_date = datetime.date.today()
    if isinstance(start_date, str):
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    if isinstance(end_date, str):
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    if not (isinstance(start_date, datetime.date) and isinstance(end_date, datetime.date)):
        raise ValueError(f'{start_date} and {end_date} should be datetime.date objects')
    delta = relativedelta(end_date, start_date)
    return delta.years, delta.months, delta.days
