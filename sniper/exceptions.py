class HttpError(Exception):
    '''
    Base class for exceptions
    '''
    status_code = 500
    detail = 'An error occurred.'


class BadRequest(HttpError):
    status_code = 400
    detail = 'bad request'
