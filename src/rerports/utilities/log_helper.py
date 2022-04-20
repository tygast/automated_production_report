"""Wrappers for better log handling"""
from functools import wraps
import inspect


def stringify_object(obj):
    if isinstance(obj, dict):
        try:
            return {stringify_object(k): stringify_object(v) for k, v in obj.items()}
        except Exception:
            return {
                repr(stringify_object(k)): stringify_object(v) for k, v in obj.items()
            }
    elif isinstance(obj, (tuple, set, list)):
        return [stringify_object(item) for item in obj]
    elif isinstance(obj, (str, int, float)):
        return obj
    else:
        return repr(obj)


def log_call(logger):
    def wrapper(func):
        func_name = f"{func.__module__}.{func.__name__}"
        sig = inspect.signature(func)

        @wraps(func)
        def wrapped(*args, **kwargs):
            string_args = {
                k: stringify_object(v)
                for k, v in sig.bind(*args, **kwargs).arguments.items()
            }
            logger.info("\n--> Calling '%s' with args:\n %s", func_name, string_args)
            try:
                result = func(*args, **kwargs)
            except Exception as err:
                logger.exception("Exception in '%s' args\n %s", func_name, string_args)
                raise err
            logger.info("\n--> Call to '%s' successful\n", func_name)
            return result

        return wrapped

    return wrapper
