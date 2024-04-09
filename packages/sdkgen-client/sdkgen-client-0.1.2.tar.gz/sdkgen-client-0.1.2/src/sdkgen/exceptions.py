class ClientException(Exception):
    pass


class KnownStatusCodeException(ClientException):
    pass


class UnknownStatusCodeException(ClientException):
    pass


class ParserException(ClientException):
    pass


class AccessTokenRequestException(ClientException):
    pass


class FoundNoAccessTokenException(ClientException):
    pass


class InvalidAccessTokenException(ClientException):
    pass


class InvalidCredentialsException(ClientException):
    pass
