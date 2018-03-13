import inspect
from functools import wraps

def message(type):
    def decorator(fn):
        fn.__message_name__ = type
        fn.__is_message = True

        @wraps(fn)
        def wrap(self, *args, **kwargs):
            return fn(self, *args, **kwargs)

        return wrap
    return decorator


class T(object):


    def __init__(self):
        self.messages = {
            fn.__message_name__: fn
            for name, fn in inspect.getmembers(
                self, predicate=inspect.ismethod
            ) if getattr(fn, '__is_message', False)
        }
        print(self.messages)


    @message('kokot')
    def t(self, data):
        print(data)

    def do(self, name, data):
        if name in self.messages:
            return self.messages[name](data)

        print('Not exists')

t = T()
t.do('kokot', 'pica')
