# -*- coding: utf-8 -*-

import math

import matplotlib.pyplot as plt
import numpy as np


def matplot_set():
    """
    设置Matplotlib的绘图参数。

    通过调用此函数，可以设置Matplotlib的绘图参数，包括图形大小等。

    参数：
        无

    返回：
        无
    """
    import matplotlib as mplt
    mplt.rcParams['figure.figsize'] = (20, 8)


def int_mark(statr: int, end: int, step: int, extract: int,
             is_replace: bool = False, is_shuffle: bool = False) -> list:
    """
    生成整数标记列表。

    根据给定的起始值、结束值、步长和抽取数量，生成一个整数标记列表。可以选择是否进行替换和洗牌。

    参数：
        statr (int): 起始值。
        end (int): 结束值。
        step (int): 步长。
        extract (int): 抽取数量。
        is_replace (bool, 可选): 是否进行放回抽样，默认为False。
        is_shuffle (bool, 可选): 是否进行洗牌，默认为False。

    返回：
        list: 生成的整数标记列表。

    异常：
        ValueError: 当起始值、结束值、步长和抽取数量不是整数类型时引发异常。
        ValueError: 当 [ start + step ] 的值小于等于 [ end ] 时引发异常。
        ValueError: 当模式 is_replace 为 False 时，步长必须大于抽取数量。
    """
    if not type(statr) == type(end) == type(step) == type(extract) == int:
        raise ValueError(' start | end | step | extract 的类型必须为 int!')

    if statr + step > end:
        raise ValueError(' [ start + step ] 必须大于 [ end ]!')

    if not is_replace and extract >= step:
        raise ValueError(' 当模式 is_replace = False 时，步长必须大于抽取数量!')

    S = math.floor(statr / step)
    E = math.ceil(end / step)

    a = list(range(step))

    ids = []

    for i in range(S, E):
        at = np.random.choice( a, size=extract, replace=is_replace )
        for t in at:
            ids.append(i * step + t)

    if is_shuffle:
        np.random.shuffle(ids)

    return ids


def id_analyst(data, steps=10, plot='pyplot'):
    """
    分析标记数据。

    根据给定的标记数据，进行分析并返回分析结果。

    参数：
        data: 标记数据。
        steps (int, 可选): 分析的步数，默认为10。
        plot (str, 可选): 绘图方式，默认为'pyplot'。

    返回：
        dict: 分析结果。

    异常：
        ImportError: 当无法导入Matlab相关模块时引发异常。
    """
    from math import log10, ceil
    d = sorted(data)
    nd_max = int(log10(d[-1]))
    nd_min = int(log10(d[0]))

    if nd_max != nd_min:
        start = 0
    else:
        start = int(d[0] / (10 ** (nd_min - 1))) * (10 ** (nd_min - 1))

    end = ceil(d[-1] / (10 ** (nd_max - 1))) * (10 ** (nd_max - 1))
    step = (end - start) / steps
    counter = [0] * (steps + 1)

    for i in d:
        counter[int((i - start) / step)] += 1

    rtn = {
        "counter": counter,
        "step": step,
        "start": start,
        "end": end
    }

    x = [i * step + start for i in range(steps + 1)]
    y = counter

    if plot == "pyplot":
        matplot_set()
        plt.plot(x, y)
        plt.show()

    elif plot == "matlab":
        import matlab
        import matlab.engine
        eng = matlab.engine.start_matlab()
        X = matlab.double(x)
        Y = matlab.double(y)
        eng.plot(X, Y)
        rtn['plot'] = eng

    return rtn
