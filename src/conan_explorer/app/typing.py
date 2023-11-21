# Typing helpers for enforced interfaces

import inspect
from types import FunctionType


class SignatureMismatchException(Exception):
    pass


class SignatureCheckMeta(type):
    def __new__(cls, name, base_classes, methods):
        """ 
        For each method, check if any base class already defined a
        method with that name. If so, make sure the signatures are the same. 
        """
        for method_name in methods:
            # allow for different constructors through factories
            if method_name == "__init__":
                continue
            method = methods[method_name]

            if not isinstance(method, FunctionType):
                continue
            for base_class in base_classes:
                try:
                    base_method = getattr(base_class, method_name)
                    base_argspec = inspect.getfullargspec(base_method)
                    method_argspec = inspect.getfullargspec(method)
                    if method_argspec != base_argspec:
                        raise SignatureMismatchException(f"{str(method_name)}\n"
                                                    f"Expected: {str(base_argspec)}\n"
                                                    f"Actual: {str(method_argspec)}")
                except AttributeError:
                    # method was not defined in base class, skip
                    continue
        return type(name, base_classes, methods)
