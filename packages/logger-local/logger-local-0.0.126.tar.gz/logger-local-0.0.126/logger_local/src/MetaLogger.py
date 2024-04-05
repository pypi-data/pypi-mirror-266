import inspect
import sys
from abc import ABCMeta
from functools import wraps
from typing import Mapping

from .LoggerLocal import Logger


class MetaLogger(type):
    @classmethod
    def __prepare__(metacls, name, bases, **kwargs) -> Mapping[str, object]:
        """This method is called before the class is created. It is used to create the class namespace."""
        return super().__prepare__(name, bases, **kwargs)

    def __new__(cls, name, bases, dct, **kwargs) -> type:
        # kwargs may be empty if the class is not instantiated with the metaclass
        if not kwargs:
            if not bases:
                raise ValueError("Please provide a logger object to the MetaLogger metaclass")
            if any(base.__name__ == "ABC" for base in bases):
                return super().__new__(cls, name, bases, dct)
            kwargs = {"object": {'bases': bases}}
        kwargs['object']['class'] = name
        kwargs['is_meta_logger'] = True
        logger = Logger.create_logger(**kwargs)
        dct['logger'] = logger

        for key, value in dct.items():
            if callable(value) and (not key.endswith("__") or key == "__init__"):  # Exclude magic methods
                dct[key] = cls.wrap_function(value, logger)

        # Add __repr__ to the class namespace, even if explicitly defined in the class
        # because otherwise logger.start in init will fail (if __repr__ is already defined)
        def __repr__(self):
            # get init arguments
            args = ", ".join(f"{k}={v!r}" for k, v in self.__dict__.items())
            return f"{self.__class__.__name__}({args})"

        dct["__repr__"] = __repr__
        return super().__new__(cls, name, bases, dct)

    @staticmethod
    def wrap_function(func: callable, logger: Logger) -> callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> any:
            # Obtain the module name of the wrapped function
            function_module = getattr(func, '__module__', None) or func.__globals__.get('__name__', 'unknown_module')

            signature = inspect.signature(func)
            arg_names = [param.name for param in signature.parameters.values()]
            if len(args) + len(kwargs) == len(arg_names) + 1:  # staticmethod called with class instance
                args = args[1:]

            kwargs_updated = {**dict(zip(arg_names, args)), **kwargs.copy()}
            extra_kwargs = {"function_name": func.__name__, "class_name": func.__qualname__.split(".")[0],
                            "filename": inspect.getfile(func) if not isinstance(
                                func, staticmethod) else inspect.getfile(func.__func__),
                            "path": f"{function_module}.{func.__qualname__}"}
            kwargs_updated["extra_kwargs"] = extra_kwargs

            full_function_name = f"{function_module}.{func.__qualname__}"
            logger.start(full_function_name, object=kwargs_updated)
            result = None
            try:
                logger.depth = 5
                result = func(*args, **kwargs)
                logger.depth = 6
            except Exception as exception:
                # Use traceback to capture frame information
                # Use sys.exc_info() to get exception information
                exc_type, exc_value, exc_traceback = sys.exc_info()
                # Extract the frame information from the traceback
                frame = (exc_traceback.tb_next or exc_traceback).tb_frame
                # Get the local variables
                locals_before_exception = frame.f_locals

                # use logger.exception if the caller is a test
                logger.error(full_function_name, object={"exception": exception,
                                                         "locals_before_exception": locals_before_exception,
                                                         "extra_kwargs": kwargs_updated})
                raise exception

            finally:
                logger.end(full_function_name, object={"result": str(result), "extra_kwargs": kwargs_updated})
            return result

        return wrapper


class ABCMetaLogger(MetaLogger, ABCMeta):
    """When using abstract class, use this class to avoid conflicts with MetaLogger.
    Example:
    from abc import ABC
    class AbstractClass(ABC, metaclass=ABCMetaLogger):
        pass
    """

    # add logger to the namespace (for typing)
    def __new__(cls, name, bases, dct, **kwargs) -> type:
        cls.logger = None
        return super().__new__(cls, name, bases, dct, **kwargs)
