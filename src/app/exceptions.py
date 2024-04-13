from shared.exceptions import APPExceptionError


class EmptyPayloadExceptionError(APPExceptionError):
    status_code = 422
    code = 'empty-payload'
    message = "You haven't sent any data"
