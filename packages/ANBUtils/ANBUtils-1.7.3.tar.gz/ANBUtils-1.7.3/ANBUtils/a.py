import warnings

import dtale


def print_rate_progress(n, s, step=0.02, message=''):
    """
    打印进度条及百分比。

    参数：
    n (int): 当前进度。
    s (int): 总进度。
    step (float, optional): 进度条步长，默认为0.02。
    message (str, optional): 附加的消息，默认为空。

    返回：
    无

    """
    if step >= 1:
        step = 0.1
    r = n / s
    t = int( r / step )
    print( "\r%s%s %.2f%% %s" % ('-' * t, '*' * (50 - t), r * 100, message), end="" )


def set_date_index(df, key):
    """
    将DataFrame的某一列转换为日期索引。

    参数：
    df (pandas.DataFrame): 需要操作的DataFrame。
    key (str): 日期列的名称。

    返回：
    pandas.DataFrame: 转换后的DataFrame。

    """
    import pandas as pd
    data = [pd.Timestamp( i ) for i in df[key]]
    del df[key]
    idx = pd.DatetimeIndex( data )
    df.set_index( idx, inplace=True )
    return df


def digit(obj):
    """
    将数字格式化为可读性更好的字符串表示。

    参数：
    obj (int or float): 需要格式化的数字。

    返回：
    tuple: 格式化后的字符串和数字的位数。

    """

    def _f(x):
        if x < 1000:
            return x

        d = ('', 'K', 'M', 'B', 'T')
        for i in range( 1, 5 ):
            x /= 1000
            if x < 1:
                return "%.2f%s" % (x * 1000, d[i - 1])
        return "%.2f%s" % (x, d[-1])

    return len( str( obj ) ), _f( obj )


def count(x):
    """
    计算列表的长度，并将长度格式化为可读性更好的字符串表示。

    参数：
    x (list): 需要计算长度的列表。

    返回：
    str: 格式化后的字符串。

    """
    length = len( x )
    return digit( length )[1]


def value(s):
    """
    从字符串中提取数字。

    参数：
    s (str): 需要提取数字的字符串。

    返回：
    list: 提取出的数字列表。

    """
    if type( s ) != str:
        return [0]
    import re
    t = re.findall( r"\d+\.?\d*", s )
    return [float( i ) for i in t]


def count2int(x):
    """
    将带有单位的数字字符串转换为对应的整数。

    参数：
    x (int or str): 需要转换的数字或字符串。

    返回：
    int: 转换后的整数。

    """
    _d = {'K': 1000, 'M': 1000000, 'B': 1000000000, 'T': 1000000000000}
    if isinstance( x, str ):
        if x[-1] in _d.keys():
            x = float( x[:-1] ) * _d[x[-1]]
        else:
            return 0
    return x


def data_browser(df, sample_size=0):
    max_sample_size = 1_000_000

    if sample_size > 0:
        if len( df ) >= sample_size > max_sample_size:
            warnings.warn( "Data sample size is too large, automatically adjusting to 1 million.", Warning )
            data = df.sample( n=max_sample_size )
        elif sample_size > len( df ):
            warnings.warn( "Data sample size is larger than data size, automatically adjusting to data size.", Warning )
            data = df
    else:
        data = df

    d = dtale.show( data )
    d.open_browser()
    return d
