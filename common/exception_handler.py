import logging
import traceback

from django.conf import settings
from rest_framework.response import Response
from rest_framework.status import HTTP_500_INTERNAL_SERVER_ERROR
from rest_framework.views import exception_handler

logger = logging.getLogger("poca_market_api")

"""
에러 처리 핸들러
"""


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if hasattr(response, "status_code") and response.status_code >= HTTP_500_INTERNAL_SERVER_ERROR:
        logger.error("Server error %s", traceback.format_exc())

    if response is not None:
        return response
    else:
        if settings.DEBUG:
            print(traceback.format_exc())
        return Response({"code": "server_error", "detail": traceback.format_exc()})
