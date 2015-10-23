from django.core.exceptions import ValidationError
from functools import wraps

# Neat trick from http://stackoverflow.com/a/14412901
def doublewrap(f):
    '''
    a decorator decorator, allowing the decorator to be used as:
    @decorator(with, arguments, and=kwargs)
    or
    @decorator
    '''
    @wraps(f)
    def new_dec(*args, **kwargs):
        if len(args) == 1 and len(kwargs) == 0 and callable(args[0]):
            # actual decorated function
            return f(args[0])
        else:
            # decorator arguments
            return lambda realf: f(realf, *args, **kwargs)

    return new_dec

@doublewrap
def field(method, validator=None):
    def parse(raw):
        return (
            (i or '').replace(u'\xa0', ' ').strip()
            for i in (raw if hasattr(raw, '__iter__') else (raw,))
        )

    def is_valid(value):
        if validator:
            try:
                validator()(value)
            except ValidationError:
                return False
        return bool(value)

    @wraps(method)
    def wrapper(*args, **kwargs):
        # If a field cannot be parsed with the specified instructions for
        # whatever reason, return it as a blank string
        try:
            for val in parse(method(*args, **kwargs)):
                if is_valid(val):
                    return val
        except Exception, e:
            pass
        return ''
    w = wrapper
    w.__field__ = True
    return w
