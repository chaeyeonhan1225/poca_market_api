from rest_framework import status
from rest_framework.exceptions import APIException


class InvalidPurchaseException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "구매할 수 없는 포토카드 입니다."
    default_code = "invalid_purchase"

    def __init__(self, detail=None, code=None):
        self.detail = detail
        self.code = code


class ConflictException(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "충돌이 발생해 수정할 수 없습니다."
    default_code = "conflict_exception"

    def __init__(self, detail=None, code=None):
        self.detail = detail
        self.code = code


class UnauthorizedException(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "권한이 없습니다."
    default_code = "unauthorized_exception"

    def __init__(self, detail=None, code=None):
        self.detail = detail
        self.code = code


class AlreadyCompletedSaleException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = '이미 판매완료 되었습니다.'
    default_code = "already_completed_sale_exception"

    def __init__(self, detail=None, code=None):
        self.detail = detail or self.default_detail
        self.code = code or self.default_code
