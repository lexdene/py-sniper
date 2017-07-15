class HttpError(Exception):
    '''
    Base class for exceptions
    '''
    status_code = 500
    detail = 'An error occurred.'


class BadRequest(HttpError):
    status_code = 400
    detail = 'bad request'


class NotFound(HttpError):
    status_code = 404
    detail = 'not found'


class MethodNotAllowed(HttpError):
    status_code = 405
    detail = 'method not allowed'
