from django.db.models import F, Min, Prefetch, Window
from django.db.models.functions import RowNumber
from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import pagination, serializers, status
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveAPIView
from rest_framework.pagination import CursorPagination
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from photocard.models import PhotoCard, PhotoCardSale, PhotoCardSaleStatus
from photocard.serializers import (PhotoCardDetailSerializer, PhotoCardSaleDetailSerializer,
                                   PhotoCardSaleParamSerializer, PhotoCardSaleSerializer, PhotoCardSerializer)
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
    permission_classes = (IsAuthenticatedOrReadOnly,)
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
                queryset=PhotoCardSale.objects.filter(status=PhotoCardSaleStatus.COMPLETED).order_by("-updated_at")[
                    0:5
                ],
                to_attr="to_completed_sales",
            )
        )


class PhotoCardSaleCursorPagination(pagination.CursorPagination):
    page_size = 10
    ordering = ("price", "-updated_at")


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        operation_summary="포토카드 판매 목록",
        operation_description="포토카드 판매 목록을 가격, 업데이트 최신순으로 조회합니다.",
        operation_id="photo_card_sale_by_photo_card",
        responses={200: PhotoCardSaleSerializer()},
    ),
)
@method_decorator(
    name="post",
    decorator=swagger_auto_schema(
        operation_summary="포토카드 판매 등록",
        operation_description="포토카드 판매를 등록합니다.",
        request_body=PhotoCardSaleParamSerializer(),
        responses={200: PhotoCardSaleSerializer()},
    ),
)
class PhotoCardSaleListCreateView(ListCreateAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = PhotoCardSaleSerializer
    pagination_class = PhotoCardSaleCursorPagination

    def get_queryset(self):
        return PhotoCardSale.objects.filter(photo_card_id=self.kwargs.get("pk"), status=PhotoCardSaleStatus.SALE)

    def create(self, request, pk):
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
    decorator=swagger_auto_schema(operation_summary="포토카드 판매 상세 조회",
                                  operation_description="포토카드 판매 상세 정보를 조회합니다. "
                                                        "거래 완료된 판매건도 조회할 수 있습니다."),
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
        except Exception as e:
            raise e
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
