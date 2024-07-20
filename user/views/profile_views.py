from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from user.serializers import UserProfileSerializer


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(operation_summary="프로필 조회", responses={200: UserProfileSerializer()}),
)
class UserProfileView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return Response(data=UserProfileSerializer(request.user).data)
