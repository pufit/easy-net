

class BaseError(Exception):
    message = 'Base error'
    code = '000'


class BadRequest(BaseError):
    message = 'Bad request'
    code = '001'


class UnhandledRequest(BaseError):
    message = 'Unhandled Request'
    code = '002'
