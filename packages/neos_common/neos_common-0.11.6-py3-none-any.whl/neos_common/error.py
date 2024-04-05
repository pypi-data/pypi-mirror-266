import typing

from web_error.error import BadRequestException, HttpException, ServerException, UnauthorisedException


class UnhandledServiceApiError(HttpException):
    pass


class ServiceApiError(HttpException):
    pass


class AuthorizationRequiredError(UnauthorisedException):
    title = "Authorization token required."


class InvalidAuthorizationError(UnauthorisedException):
    title = "Authorization token invalid."


class InsufficientPermissionsError(UnauthorisedException):
    title = "Insufficient permissions."


class InvalidResourceFormatError(BadRequestException):
    title = "Resource has invalid format."


class IdentityAccessManagerError(ServerException):
    code = "identity-access-manager-error"
    title = "Problem with Identity Access Manager."


class ServiceConnectionError(HttpException):
    code = "service-connection-error"
    status = 500

    def __init__(self, title: str, details: typing.Union[str, None] = None) -> None:
        super().__init__(title, details=details, code=self.code, status=self.status)


class ServiceTimeoutError(HttpException):
    code = "service-timeout-error"
    status = 500

    def __init__(self, title: str, details: typing.Union[str, None] = None) -> None:
        super().__init__(title, details=details, code=self.code, status=self.status)


class SignatureError(UnauthorisedException):
    code = "signature-error"
    title = "Signature invalid."
