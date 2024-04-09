from functools import wraps


def restrict_arguments(*forbidden_args):
    """
    A decorator that disallows specific named arguments for a class method.

    Args:
        *forbidden_args (str): Arguments that are not allowed to be passed.

    Usage:
        ```
        @disallow_arguments("arg1", "arg2")
        def some_method(self, **kwargs):
            ...
        ```
    """
    def decorator(func):
        @wraps(func)
        def wrapper(cls, **kwargs):
            for arg in forbidden_args:
                if arg in kwargs:
                    raise ValueError(f"Overriding the '{arg}' field is not allowed.")
            return func(cls, **kwargs)
        return wrapper
    return decorator
