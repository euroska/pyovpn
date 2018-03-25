from functools import wraps
from .errors import AdminRequired, AuthenticationRequired

def isAdmin(fn):
    @wraps(fn)
    async def wrapper(self, body, user):
        if not user['is_admin']:
            raise AdminRequired()

        return await fn(self, body, user)

    return wrapper


def isAutorized(fn):
    @wraps(fn)
    async def wrapper(self, body, user):
        if user['is_anonymouse']:
            raise AuthenticationRequired()

        return await fn(self, body, user)

    return wrapper


def api(message_in, schema_in={}, message_out=None, schema_out={}):
    def wrapper(fn):
        fn.__api__ = True
        fn.__message_in__ = message_in
        fn.__message_out__ = message_out or message_in
        fn.__schema_in__ = schema_in
        fn.__schema_out__ = schema_out
        return fn

    return wrapper
