from rest_framework import status
from rest_framework.exceptions import APIException


class NotEnoughCashException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "잔액이 부족합니다."
    default_code = "not_enough_cash"

    def __init__(self, detail=None, code=None):
        self.detail = detail
        self.code = code
