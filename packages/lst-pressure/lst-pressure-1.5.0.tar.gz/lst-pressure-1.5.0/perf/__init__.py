"""
perf
"""
import datetime
import functools
import time
from conf import Conf, LogLevel
from logger import debug

module_import_time = datetime.datetime.now()
conf = Conf()

fn_runtime = {}


def monitor_perf(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if conf.LOG_LEVEL == LogLevel.DEBUG:
            debug(f"\n\n*** PERFORMANCE STATS ***")

            # Runtime
            end_time = datetime.datetime.now()
            duration = end_time - module_import_time
            debug(f"Total runtime: {duration}")

            # Find the length of the longest function identifier
            max_key_length = max(len(func_identifier) for func_identifier in fn_runtime)

            # Find the maximum length of call_count when converted to string
            max_call_count_length = max(
                len(str(call_count)) for _, (_, call_count) in fn_runtime.items()
            )

            # Sort items by total runtime in descending order
            sorted_items = sorted(fn_runtime.items(), key=lambda item: item[1][0], reverse=True)

            # Print each entry with padding for alignment
            for func_identifier, (total_runtime, call_count) in sorted_items:
                padded_func_identifier = func_identifier.ljust(max_key_length + 1)
                padded_call_count = str(call_count).rjust(max_call_count_length)
                debug(
                    f" :: {padded_func_identifier} {total_runtime:.4f} seconds : {padded_call_count} calls"
                )
        return result

    return wrapper


def track_total_runtime(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()

        if conf.LOG_LEVEL == LogLevel.DEBUG:
            # Construct a unique key using module name and function name
            unique_key = f"{func.__module__}.{func.__name__}"

            # Update cumulative runtime and call count in the global dictionary
            runtime = end_time - start_time
            if unique_key in fn_runtime:
                fn_runtime[unique_key] = (
                    fn_runtime[unique_key][0] + runtime,
                    fn_runtime[unique_key][1] + 1,
                )
            else:
                fn_runtime[unique_key] = (runtime, 1)
        return result

    return wrapper


def decorate_all(decorator):
    def decorate(cls):
        for attr_name, attr_value in cls.__dict__.items():
            if isinstance(attr_value, staticmethod):
                # Unwrap the static method, decorate it, and then re-wrap it
                original_func = attr_value.__func__
                decorated_func = decorator(original_func)
                setattr(cls, attr_name, staticmethod(decorated_func))
            elif isinstance(attr_value, classmethod):
                # Unwrap the class method, decorate it, and then re-wrap it
                original_func = attr_value.__func__
                decorated_func = decorator(original_func)
                setattr(cls, attr_name, classmethod(decorated_func))
            elif isinstance(attr_value, property):
                # Apply the decorator to the getter, and re-create the property
                original_get = attr_value.fget
                decorated_get = decorator(original_get) if original_get else None
                original_set = attr_value.fset
                decorated_set = decorator(original_set) if original_set else None
                original_del = attr_value.fdel
                decorated_del = decorator(original_del) if original_del else None
                setattr(
                    cls,
                    attr_name,
                    property(decorated_get, decorated_set, decorated_del, attr_value.__doc__),
                )
            elif callable(attr_value):
                # Regular method
                setattr(cls, attr_name, decorator(attr_value))
        return cls

    return decorate


__all__ = ["monitor_perf", "track_total_runtime", "decorate_all"]

# Automatically added by katversion
__version__ = '1.5.0'
