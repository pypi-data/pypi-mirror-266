import pickle
from sys import getsizeof


def easy_dump(obj, file_name):
    """
    将对象以pickle格式保存到文件中。

    参数:
        obj: 要保存的对象。
        file_name: 保存的文件名，如果没有以'.pkl'结尾，会自动添加后缀。

    返回:
        无。
    """
    if not file_name.endswith('.pkl'):
        file_name += '.pkl'
    with open(file_name, 'wb') as file:
        pickle.dump(obj, file)


def easy_load(file_name: str):
    """
    从pickle文件中加载对象。

    参数:
        file_name: 要加载的文件名，如果没有以'.pkl'结尾，会自动添加后缀。

    返回:
        加载的对象。
    """
    if not file_name.endswith('.pkl'):
        file_name += '.pkl'
    with open(file_name, 'rb') as file:
        obj = pickle.load(file)
        print('object type:', type(obj))
        print('object size: ', getsizeof(obj))
        return obj
