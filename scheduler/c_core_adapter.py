"""Thin ctypes adapter for the optional C DSA core."""

import ctypes
import os
from datetime import datetime

from django.utils import timezone

_STRATEGY_CODE = {'priority': 0, 'fifo': 1, 'lifo': 2}
_LIB = None
_LOAD_ERROR = None


def _library_path():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(base_dir, 'c_core', 'libscheduler_dsa.so')


def _load_library():
    global _LIB, _LOAD_ERROR
    if _LIB is not None or _LOAD_ERROR is not None:
        return _LIB

    lib_path = _library_path()
    if not os.path.exists(lib_path):
        _LOAD_ERROR = f'missing library at {lib_path}'
        return None

    try:
        lib = ctypes.CDLL(lib_path)
        lib.ccore_order_indices.argtypes = [
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_double),
            ctypes.POINTER(ctypes.c_double),
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_int),
        ]
        lib.ccore_order_indices.restype = ctypes.c_int

        lib.ccore_simulate_strategy.argtypes = [
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_double),
            ctypes.POINTER(ctypes.c_double),
            ctypes.POINTER(ctypes.c_double),
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_int),
            ctypes.POINTER(ctypes.c_double),
        ]
        lib.ccore_simulate_strategy.restype = ctypes.c_int
        _LIB = lib
    except OSError as exc:
        _LOAD_ERROR = str(exc)
        return None

    return _LIB


def c_core_available():
    return _load_library() is not None


def _to_timestamp(value):
    if isinstance(value, datetime):
        dt = value
    elif isinstance(value, str):
        dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
    else:
        dt = timezone.now()

    if dt.tzinfo is None:
        dt = timezone.make_aware(dt)
    return dt.timestamp()


def order_tasks(strategy, tasks):
    if not tasks:
        return []

    lib = _load_library()
    if not lib or strategy not in _STRATEGY_CODE:
        return _python_order(strategy, tasks)

    size = len(tasks)
    priority = (ctypes.c_double * size)(*[float(t.priority_score) for t in tasks])
    created = (ctypes.c_double * size)(*[_to_timestamp(t.created_at) for t in tasks])
    out = (ctypes.c_int * size)()

    rc = lib.ccore_order_indices(_STRATEGY_CODE[strategy], priority, created, size, out)
    if rc != 0:
        return _python_order(strategy, tasks)

    return [tasks[out[i]] for i in range(size)]


def simulate_strategy(strategy, tasks):
    if not tasks:
        return {'completed_count': 0, 'average_wait_hours': 0.0}

    lib = _load_library()
    if not lib or strategy not in _STRATEGY_CODE:
        return _python_simulate(strategy, tasks)

    size = len(tasks)
    priority = (ctypes.c_double * size)(*[float(t.priority_score) for t in tasks])
    created = (ctypes.c_double * size)(*[_to_timestamp(t.created_at) for t in tasks])
    effort = (ctypes.c_double * size)(*[float(t.estimated_effort) for t in tasks])
    completed = ctypes.c_int(0)
    average_wait = ctypes.c_double(0.0)

    rc = lib.ccore_simulate_strategy(
        _STRATEGY_CODE[strategy],
        priority,
        created,
        effort,
        size,
        ctypes.byref(completed),
        ctypes.byref(average_wait),
    )
    if rc != 0:
        return _python_simulate(strategy, tasks)

    return {
        'completed_count': int(completed.value),
        'average_wait_hours': round(float(average_wait.value), 2),
    }


def _python_order(strategy, tasks):
    ordered = list(tasks)
    if strategy == 'priority':
        return sorted(ordered, key=lambda t: t.priority_score)
    if strategy == 'fifo':
        return sorted(ordered, key=lambda t: t.created_at)
    if strategy == 'lifo':
        return sorted(ordered, key=lambda t: t.created_at, reverse=True)
    return ordered


def _python_simulate(strategy, tasks):
    ordered = _python_order(strategy, tasks)
    wait_sum = 0.0
    elapsed = 0.0
    for task in ordered:
        wait_sum += elapsed
        elapsed += float(task.estimated_effort)
    return {
        'completed_count': len(ordered),
        'average_wait_hours': round(wait_sum / len(ordered), 2),
    }
