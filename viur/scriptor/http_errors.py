from .file import File


class HTTPException(Exception):
    """
        Base-Class for all Exceptions that should match to an http error-code
    """

    def __init__(self, status: int, name: str, descr: str, response: File):
        """
        :param status: The desired http error-code (404, 500, ...)
        :param name: Name as of RFC 2616
        :param descr: Human-readable description of that error
        """
        super(HTTPException, self).__init__()
        self.status = status
        self.name = name
        self.descr = descr
        self.response = response

    def __str__(self):
        return str(self.descr)


class BadRequest(HTTPException):
    """
        BadRequest
    """

    def __init__(
        self,
        descr: str = "The request your browser sent cannot be fulfilled due to bad syntax.",
        response: File = None
    ):
        super(BadRequest, self).__init__(status=400, name="Bad Request", descr=descr, response=response)


class Unauthorized(HTTPException):
    """
        Unauthorized

        Raised whenever a request hits an path protected by canAccess() or a canAdd/canEdit/... -Function inside
        an application returns false.
    """

    def __init__(
        self,
        descr: str = "The resource is protected and you don't have the permissions.",
        response: File = None
    ):
        super(Unauthorized, self).__init__(status=401, name="Unauthorized", descr=descr, response=response)


class PaymentRequired(HTTPException):
    """
        PaymentRequired

        Not used inside viur.core. This status-code is reserved for further use and is currently not
        supported by clients.
    """

    def __init__(
        self,
        descr: str = "Payment Required",
        response: File = None
    ):
        super(PaymentRequired, self).__init__(status=402, name="Payment Required", descr=descr, response=response)


class Forbidden(HTTPException):
    """
        Forbidden

        Not used inside viur.core. May be utilized in the future to distinguish between requests from
        guests and users, who are logged in but don't have the permission.
    """

    def __init__(
        self,
        descr: str = "The resource is protected and you don't have the permissions.",
        response: File = None
    ):
        super(Forbidden, self).__init__(status=403, name="Forbidden", descr=descr, response=response)


class NotFound(HTTPException):
    """
        NotFound

        Usually raised in view() methods from application if the given key is invalid.
    """

    def __init__(
        self,
        descr: str = "The requested resource could not be found.",
        response: File = None
    ):
        super(NotFound, self).__init__(status=404, name="Not Found", descr=descr, response=response)


class MethodNotAllowed(HTTPException):
    """
        MethodNotAllowed

        Raised if a function is accessed which doesn't have the @exposed / @internalExposed decorator or
        if the request arrived using get, but the function has the @forcePost flag.
    """

    def __init__(
        self,
        descr: str = "Method Not Allowed",
        response: File = None
    ):
        super(MethodNotAllowed, self).__init__(status=405, name="Method Not Allowed", descr=descr, response=response)


class NotAcceptable(HTTPException):
    """
        NotAcceptable

        Signals that the parameters supplied doesn't match the function signature
    """

    def __init__(
        self,
        descr: str = "The request cannot be processed due to missing or invalid parameters.",
        response: File = None
    ):
        super(NotAcceptable, self).__init__(status=406, name="Not Acceptable", descr=descr, response=response)


class RequestTimeout(HTTPException):
    """
        RequestTimeout

        This must be used for the task api to indicate it should retry
    """

    def __init__(
        self,
        descr: str = "The request has timed out.",
        response: File = None
    ):
        super(RequestTimeout, self).__init__(status=408, name="Request Timeout", descr=descr, response=response)


class Gone(HTTPException):
    """
    Gone

    The 410 (Gone) status code indicates that access to the target
    resource is no longer available at the origin server and that this
    condition is likely to be permanent.  If the origin server does not
    know, or has no facility to determine, whether or not the condition
    is permanent, the status code 404 (Not Found) ought to be used
    instead.

    See https://datatracker.ietf.org/doc/html/rfc7231#section-6.5.9
    """

    def __init__(
        self,
        descr: str = "Gone",
        response: File = None
    ):
        super(Gone, self).__init__(status=410, name="Gone", descr=descr, response=response)


class PreconditionFailed(HTTPException):
    """
        PreconditionFailed

        Mostly caused by a missing/invalid securitykey.
    """

    def __init__(
        self,
        descr: str = "Precondition Failed",
        response: File = None
    ):
        super(PreconditionFailed, self).__init__(status=412, name="Precondition Failed", descr=descr, response=response)


class RequestTooLarge(HTTPException):
    """
        RequestTooLarge

        Not used inside viur.core
    """

    def __init__(
        self,
        descr: str = "Request Too Large",
        response: File = None
    ):
        super(RequestTooLarge, self).__init__(status=413, name="Request Too Large", descr=descr, response=response)


class Locked(HTTPException):
    """
        Locked

        Raised if a resource cannot be deleted due to incomming relational locks
    """

    def __init__(
        self,
        descr: str = "Ressource is Locked",
        response: File = None
    ):
        super(Locked, self).__init__(status=423, name="Ressource is Locked", descr=descr, response=response)


class TooManyRequests(HTTPException):
    """
        Too Many Requests

        The 429 status code indicates that the user has sent too many
        requests in a given amount of time ("rate limiting").
    """

    def __init__(
        self,
        descr: str = "Too Many Requests",
        response: File = None
    ):
        super(TooManyRequests, self).__init__(status=429, name="Too Many Requests", descr=descr, response=response)


class UnprocessableEntity(HTTPException):
    """
    Unprocessable Entity

    The 422 (Unprocessable Entity) status code means the server
    understands the content type of the request entity (hence a
    415 (Unsupported Media Type) status code is inappropriate), and the
    syntax of the request entity is correct (thus a 400 (Bad Request)
    status code is inappropriate) but was unable to process the contained
    instructions.
    For example, this error condition may occur if an XML
    request body contains well-formed (i.e., syntactically correct), but
    semantically erroneous, XML instructions

    See https://www.rfc-editor.org/rfc/rfc4918#section-11.2
    """

    def __init__(
        self,
        descr: str = "Unprocessable Entity",
        response: File = None
    ):
        super().__init__(status=422, name="Unprocessable Entity", descr=descr, response=response)


class Censored(HTTPException):
    """
        Censored

        Not used inside viur.core
    """

    def __init__(
        self,
        descr: str = "Unavailable For Legal Reasons",
        response: File = None
    ):
        super(Censored, self).__init__(status=451, name="Unavailable For Legal Reasons", descr=descr, response=response)


class InternalServerError(HTTPException):
    """
        InternalServerError

        The catch-all error raised by the server if your code raises any python-exception not deriving from
        HTTPException
    """

    def __init__(
        self,
        descr: str = "Internal Server Error",
        response: File = None
    ):
        super(InternalServerError, self).__init__(status=500, name="Internal Server Error", descr=descr,
                                                  response=response)


class NotImplemented(HTTPException):
    """
        NotImplemented

        Not really implemented at the moment :)
    """

    def __init__(
        self,
        descr: str = "Not Implemented",
        response: File = None
    ):
        super(NotImplemented, self).__init__(status=501, name="Not Implemented", descr=descr, response=response)


class BadGateway(HTTPException):
    """
        BadGateway

        Not used inside viur.core
    """

    def __init__(
        self,
        descr: str = "Bad Gateway",
        response: File = None
    ):
        super(BadGateway, self).__init__(status=502, name="Bad Gateway", descr=descr, response=response)


class ServiceUnavailable(HTTPException):
    """
        ServiceUnavailable

        Not used inside viur.core
    """

    def __init__(
        self,
        descr: str = "Service Unavailable",
        response: File = None
    ):
        super(ServiceUnavailable, self).__init__(status=503, name="Service Unavailable", descr=descr, response=response)


def get_exception_by_code(code: int = 0) -> HTTPException:
    exceptions = {
        400: BadRequest,
        401: Unauthorized,
        402: PaymentRequired,
        403: Forbidden,
        404: NotFound,
        405: MethodNotAllowed,
        406: NotAcceptable,
        408: RequestTimeout,
        410: Gone,
        412: PreconditionFailed,
        413: RequestTooLarge,
        422: UnprocessableEntity,
        423: Locked,
        429: TooManyRequests,
        451: Censored,
        500: InternalServerError,
        501: NotImplemented,
        502: BadGateway,
        503: ServiceUnavailable,
    }
    return exceptions.get(code)
