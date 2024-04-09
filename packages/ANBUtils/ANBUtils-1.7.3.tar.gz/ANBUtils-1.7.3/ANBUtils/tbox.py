# -*- coding:UTF-8 -*-

import time
from datetime import datetime, timedelta


def future(x):
    """
    计算未来日期。

    根据给定的天数偏移量，计算未来的日期。

    参数：
        x (int): 天数偏移量。

    返回：
        str: 未来日期的字符串表示（格式：YYYY-MM-DD）。

    异常：
        None
    """
    return (datetime.now() + timedelta( days=x )).strftime( '%Y-%m-%d' )


def utc2tz(dt, tz='E8'):
    """
    将UTC时间转换为指定时区的时间。

    根据给定的UTC时间和时区偏移量，将UTC时间转换为指定时区的时间。

    参数：
        dt (datetime): UTC时间。
        tz (str): 时区偏移量（默认为'E8'，表示东八区）。

    返回：
        datetime: 指定时区的时间。

    异常：
        ValueError: 当时区偏移量不在'E0'至'W12'范围内时，引发该异常。
    """
    if tz[0].upper() == 'E':
        h = int( tz[1:] )
    elif tz[0].upper() == 'W':
        h = int( tz[1:] ) * -1
    else:
        raise ValueError( '[utc2tz] tz is KeyError!' )

    return dt + timedelta( hours=h )


def today():
    """
    获取当前日期。

    返回：
        str: 当前日期的字符串表示（格式：YYYY-MM-DD）。

    异常：
        None
    """
    return datetime.now().strftime( "%Y-%m-%d" )


def tomorrow():
    """
    获取明天的日期。

    返回：
        str: 明天的日期的字符串表示（格式：YYYY-MM-DD）。

    异常：
        None
    """
    return future( 1 )


def yesterday():
    """
    获取昨天的日期。

    返回：
        str: 昨天的日期的字符串表示（格式：YYYY-MM-DD）。

    异常：
        None
    """
    return future( -1 )


def now():
    """
    获取当前日期和时间。

    返回：
        str: 当前日期和时间的字符串表示（格式：YYYY-MM-DD HH:MM）。

    异常：
        None
    """
    return datetime.now().strftime( '%Y-%m-%d %H:%M' )


def future_base(date, x):
    """
    根据基准日期计算未来日期。

    根据给定的基准日期和天数偏移量，计算未来的日期。

    参数：
        date (str): 基准日期的字符串表示（格式：YYYY-MM-DD）。
        x (int): 天数偏移量。

    返回：
        str: 未来日期的字符串表示（格式：YYYY-MM-DD）。

    异常：
        None
    """
    base = datetime.strptime( date, "%Y-%m-%d" )
    return (base + timedelta( days=x )).strftime( '%Y-%m-%d' )


def ts2str(x):
    """
    将时间戳转换为日期字符串。

    根据给定的时间戳，将其转换为日期字符串（格式：YYYY-MM-DD）。

    参数：
        x (int or str): 时间戳。

    返回：
        str: 日期字符串（格式：YYYY-MM-DD）。

    异常：
        None
    """
    if type( x ) == str:
        x = int( x )
    return time.strftime( "%Y-%m-%d", time.localtime( x ) )


def date_format(date, date_format='YYYY-MM-DD'):
    """
    格式化日期字符串。

    根据给定的日期字符串和日期格式，将日期字符串格式化为指定的日期格式。

    参数：
        date (str): 日期字符串。
        date_format (str): 日期格式（默认为'YYYY-MM-DD'）。

    返回：
        str: 格式化后的日期字符串。

    异常：
        None
    """
    if len( date ) == 10:
        if len( date.split( '-' ) ) == 3:
            date = date
        elif len( date.split( '/' ) ) == 3:
            date = date.replace( '/', '-' )
        elif len( date.split( '_' ) ) == 3:
            date = date.replace( '_', '-' )

    if len( date ) == 6:
        y = date[:2]
        m = date[2:4]
        d = date[4:]
        if int( y ) <= 30:
            y = '20' + y
        else:
            y = '19' + y
        date = '-'.join( [y, m, d] )

    if date_format == 'YYYY-MM-DD':
        return date
    elif date_format == 'YYMMDD':
        return date.replace( '-', '' )[2:]
    elif date_format == 'YYYY_MM_DD':
        return date.replace( '-', '_' )


def previous_date(n, base_day=None, mode='m'):
    if base_day is None:
        base_day = datetime.today()
    else:
        base_day = datetime.strptime( base_day, '%Y-%m-%d' )

    if mode == 'm':
        pass

    elif mode == 'q':
        current_month = base_day.month
        base_day = datetime( base_day.year, ((current_month - 1) // 3) * 3 + 1, 1 )

    else:
        raise ValueError( 'mode must be m or q' )

    # 获取当前月份的年份和月份
    current_year, current_month = base_day.year, base_day.month

    # 计算当前月份之前的n个月
    n = n if mode == 'm' else n * 3
    for _ in range( n ):
        # 减去一个月
        if current_month == 1:
            current_month = 12
            current_year -= 1
        else:
            current_month -= 1

    # 得到所需日期
    _date = datetime( current_year, current_month, 1 )

    return _date
