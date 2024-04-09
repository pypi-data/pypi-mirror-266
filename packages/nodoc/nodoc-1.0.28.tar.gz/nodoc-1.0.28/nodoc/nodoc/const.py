import os, psutil
from typing import Literal, TypeAlias, NewType, TypeVar, List

def __import():
    global ndarray, Tensor
    from numpy import ndarray
    from torch import Tensor

Embedding = TypeVar('Embedding', 'ndarray', 'Tensor', list['Tensor'])

def get_size(size: int, mode: Literal['str', 'tuple'] = 'str'):
    unit: list[str] = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    __size = float(size)
    while __size > 1024.0 and len(unit) > 1:
        __size /= 1024.0
        unit.pop(0)
    match mode:
        case 'str':
            return f"{__size}{unit[0]}"
        case 'tuple':
            return (__size, unit[0])

def show_memory_info():
    pid = os.getpid()
    process = psutil.Process(pid)
    info = process.memory_full_info()
    memory = info.vms
    return memory

class c_source:
    directory = os.path.join(os.path.dirname(__file__), 'c_source')
    vectordb = os.path.join(directory, 'vectordb.dll')