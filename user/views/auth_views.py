import logging

from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from user.serializers import UserLoginSerializer, UserRegisterSerializer

logger = logging.getLogger("poca_market_api")
@method_decorator(
    name="post",
    decorator=swagger_auto_schema(operation_summary="회원가입", request_body=UserRegisterSerializer()),
)
class UserRegisterView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = TokenObtainPairSerializer.get_token(user)
        logger.info(f'{user.email}({user.id}) registered successfully')
        return Response({"user": serializer.data, "token": {"access": str(token.access_token), "refresh": str(token)}})


@method_decorator(
    name="post",
    decorator=swagger_auto_schema(operation_summary="로그인", request_body=TokenObtainPairSerializer()),
)
class UserLoginView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        token_serializer = TokenObtainPairSerializer(data=request.data)
        token_serializer.is_valid(raise_exception=True)
        user = token_serializer.user
        serializer = UserLoginSerializer(user)
        logger.info(f'{user.email}({user.id}) logged in successfully')
        return Response({"user": serializer.data, "token": token_serializer.validated_data}, status=status.HTTP_200_OK)
