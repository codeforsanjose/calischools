from functools import wraps

def field(method):
    @wraps(method)
    def wrapper(obj):
        # If a field cannot be parsed with the specified instructions for
        # whatever reason, return it as a blank string
        try:
            result = method(obj).replace(u'\xa0', ' ').strip()
        except:
            return ''
        return result
    w = wrapper
    w.__field__ = True
    return w
