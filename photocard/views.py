from django.db.models import Min, Prefetch, Window, F
from django.db.models.functions import RowNumber
from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveAPIView
from rest_framework.pagination import CursorPagination
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from photocard.models import PhotoCard, PhotoCardSale, PhotoCardSaleStatus
from photocard.serializers import (
    PhotoCardDetailSerializer,
    PhotoCardSaleDetailSerializer,
    PhotoCardSaleParamSerializer,
    PhotoCardSaleSerializer,
    PhotoCardSerializer,
)
from photocard.services.photo_card_sale_purchase_service import PhotoCardSalePurchaseService
from photocard.services.photo_card_sale_service import PhotoCardSaleService


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(operation_summary="포토카드 목록 조회"),
)
@method_decorator(
    name="post",
    decorator=swagger_auto_schema(operation_summary="포토카드 등록", request_body=PhotoCardSerializer()),
)
class PhotoCardListCreateView(ListCreateAPIView):
    serializer_class = PhotoCardSerializer
    permission_classes = (AllowAny,)
    parser_classes = (MultiPartParser,)

    def get_queryset(self):
        return PhotoCard.objects.annotate(min_price=Min("photocardsale__price"))


"""
photo_card_id가 같으면 가격이 최소인 row를 가져온다.
"""


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(operation_summary="판매중인 포토카드 판매 목록"),
)
class PhotoCardSaleListView(ListAPIView):
    serializer_class = PhotoCardSaleSerializer
    permission_classes = (AllowAny,)

    # TODO: 쿼리 개선 필요

    def get_queryset(self):
        return (
            PhotoCardSale.objects.filter(status=PhotoCardSaleStatus.SALE)
            .annotate(
                row_number=Window(
                    expression=RowNumber(),
                    order_by=[F("price"), F("updated_at")],
                    partition_by=[F("photo_card_id")],
                )
            )
            .filter(row_number=1)
        )


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(operation_summary="포토카드 상세"),
)
class PhotoCardDetailView(RetrieveAPIView):
    serializer_class = PhotoCardDetailSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        return PhotoCard.objects.prefetch_related(
            Prefetch(
                lookup="photocardsale_set",
                queryset=PhotoCardSale.objects.filter(status=PhotoCardSaleStatus.COMPLETED).order_by("-updated_at"),
                to_attr="to_completed_sales",
            )
        )


@method_decorator(
    name="post",
    decorator=swagger_auto_schema(
        operation_summary="포토카드 판매 등록",
        request_body=PhotoCardSaleParamSerializer(),
        responses={200: PhotoCardSaleSerializer()},
    ),
)
class PhotoCardSaleCreateView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk):
        try:
            photo_card = PhotoCard.objects.get(id=pk)
            serializer = PhotoCardSaleParamSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            result = PhotoCardSaleService(photo_card=photo_card, seller=request.user).create(
                price=serializer.validated_data["price"]
            )
            return Response(PhotoCardSaleSerializer(result).data)
        except PhotoCard.DoesNotExist as e:
            return Response(data={"detail": "존재하지 않는 포토카드 입니다."}, status=status.HTTP_404_NOT_FOUND)


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(operation_summary="포토카드 판매 상세 조회"),
)
@method_decorator(
    name="patch",
    decorator=swagger_auto_schema(operation_summary="포토카드 가격 수정", request_body=PhotoCardSaleParamSerializer()),
)
class PhotoCardSaleDetailView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        photo_card_id = kwargs.get("pk")
        photo_card_sale_id = kwargs.get("sale_id")
        try:
            photo_card_sale = PhotoCardSale.objects.select_related("buyer", "seller").get(
                uuid=photo_card_sale_id, photo_card_id=photo_card_id
            )
            return Response(data=PhotoCardSaleDetailSerializer(photo_card_sale).data)
        except PhotoCardSale.DoesNotExist:
            return Response(data={"detail": "존재하지 않는 포토카드 판매건입니다."}, status=status.HTTP_404_NOT_FOUND)

    """
    가격을 수정한다.
    """

    def patch(self, request, *args, **kwargs):
        photo_card_id = kwargs.get("pk")
        photo_card_sale_id = kwargs.get("sale_id")
        serializer = PhotoCardSaleParamSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            photo_card = PhotoCard.objects.get(id=photo_card_id)

            sale = PhotoCardSaleService(photo_card=photo_card, seller=request.user).update_price(
                sale_id=photo_card_sale_id, price=serializer.validated_data["price"]
            )
            return Response(data=PhotoCardSaleDetailSerializer(sale).data)
        except PhotoCard.DoesNotExist:
            return Response(data={"detail": "존재하지 않는 포토카드 입니다."}, status=status.HTTP_404_NOT_FOUND)
        except PhotoCardSale.DoesNotExist:
            return Response(data={"detail": "존재하지 않는 판매건 입니다."}, status=status.HTTP_404_NOT_FOUND)


@method_decorator(
    name="post",
    decorator=swagger_auto_schema(operation_summary="포토카드 구매"),
)
class PhotoCardSalePurchaseView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        photo_card_id = kwargs.get("pk")
        sale_id = kwargs.get("sale_id")

        try:
            sale = PhotoCardSale.objects.get(uuid=sale_id, photo_card_id=photo_card_id)
            result = PhotoCardSalePurchaseService(photo_card_sale=sale, buyer=request.user).purchase()
            return Response(data=PhotoCardSaleDetailSerializer(result).data)
        except PhotoCardSale.DoesNotExist:
            return Response(data={"detail": "존재하지 않는 판매건 입니다."}, status=status.HTTP_404_NOT_FOUND)
