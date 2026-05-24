from rest_framework.exceptions import APIException


class ApplicationError(APIException):
    status_code = 400
    default_detail = 'Application Error'
    default_code = "application_code"