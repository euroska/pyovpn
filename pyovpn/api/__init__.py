import sys
import inspect
import jsonschema
import traceback
import logging
from .auth import AuthApi
from .template_server import TemplateServerApi
from .template_user import TemplateUserApi
from .vpn import VpnApi
from .user import UserApi
from .decorators import api
from .errors import ApiError, MessageNotImplemented, InternalError, SchemaError

logger = logging.getLogger(__name__)


class Api(AuthApi, UserApi, TemplateServerApi, TemplateUserApi, VpnApi):

    def __init__(self, manager):
        '''
        '''
        self.manager = manager
        self.methods = {}
        self.schemas_in = {}
        self.schemas_out = {}
        self.reply = {}

        for method, fn in inspect.getmembers(self, predicate=inspect.ismethod):
            if hasattr(fn, '__api__'):
                self.methods[fn.__message_in__] = fn
                self.schemas_in[fn.__message_in__] = fn.__schema_in__
                self.schemas_out[fn.__message_out__] = fn.__schema_out__
                self.reply[fn.__message_in__] = fn.__message_out__

    async def __call__(self, message, body, user):
        '''
        Router method
        '''
        try:
            if message in self.methods:
                schema = self.schemas_in[message]
                if schema:
                    jsonschema.validate(body, schema)

                body = await self.methods[message](body, user)
                reply = self.reply[message]
                schema = self.schemas_out[reply]
                if schema and self.manager.config['debug']:
                    jsonschema.validate(body, schema)

                return {
                    'message': reply,
                    'body': body,
                }
            else:
                raise MessageNotImplemented()

        except ApiError as e:
            return e.json()

        except jsonschema.ValidationError as e:
            return SchemaError(e).json()

        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            return InternalError(e).json()

    @api('pyovpn.messages')
    async def messages(self, body, user):
        return {
            'in': self.schemas_in,
            'out': self.schemas_out,
        }

    @api('pyovpn.error')
    async def error(self, body, user):
        raise Exception('Common error')
