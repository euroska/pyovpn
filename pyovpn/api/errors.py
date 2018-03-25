class ApiError(Exception):
    def __init__(self, code, description):
        self.code = code
        self.description = description

    def json(self):
        return {
            'message': 'pyovpn.error',
            'body': {
                'code': self.code,
                'description': self.description,
            }
        }


class AuthenticationRequired(ApiError):
    def __init__(self):
        super(AuthenticationRequired, self).__init__(
            code='pyovpn.error.authentication_permission',
            description='You must be logged',
        )


class AdminRequired(ApiError):
    def __init__(self):
        super(AdminRequired, self).__init__(
            code='pyovpn.error.insufficient_permission',
            description='You must be admin',
        )


class MessageNotImplemented(ApiError):
    def __init__(self):
        super(MessageNotImplemented, self).__init__(
            code='pyovpn.error.not_implemented',
            description='Api message was not be implemented',
        )


class SchemaError(ApiError):
    def __init__(self, e):
        super(InternalError, self).__init__(
            code='pyovpn.error.schema',
            description=str(e),
        )


class InternalError(ApiError):
    def __init__(self, e):
        super(InternalError, self).__init__(
            code='pyovpn.error.internal_error',
            description=str(e),
        )
