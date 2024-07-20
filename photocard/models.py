import os
import uuid
from enum import unique

from django.conf import settings
from django.db import models
from django.contrib.postgres.indexes import BrinIndex
from django.utils import timezone
from enumfields import Enum, EnumField

from common.models import TimeRecordingMixin


def upload_photo_card_to(_instance, filename):
    prefix = timezone.now().strftime("%Y/%m/%d")
    return settings.PHOTO_CARD_STORE_DIRECTORY + "/" + prefix + "/" + filename


@unique
class PhotoCardType(Enum):
    ALBUM = "ALBUM"
    EVENT = "EVENT"
    COLLABORATION = "COLLABORATION"
    ETC = "ETC"

    class Labels:
        ALBUM = "앨범"
        EVENT = "특전"
        COLLABORATION = "콜라보"
        ETC = "기타"


class PhotoCard(TimeRecordingMixin):
    image = models.ImageField(upload_to=upload_photo_card_to, verbose_name="포토카드 대표 이미지")
    artist = models.CharField(max_length=20, verbose_name="아티스트")
    title = models.CharField(max_length=150, verbose_name="포토카드 명")
    type = EnumField(PhotoCardType, default=PhotoCardType.ALBUM, max_length=20, verbose_name="포토카드 타입")

    class Meta:
        db_table = "photo_card"
        verbose_name = "포토카드"
        indexes = [BrinIndex(fields=["updated_at"])]


@unique
class PhotoCardSaleStatus(Enum):
    SALE = "SALE"
    COMPLETED = "COMPLETED"

    class Labels:
        SALE = "판매중"
        COMPLETED = "판매 완료"


# 포토 카드 판매
class PhotoCardSale(TimeRecordingMixin):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    photo_card = models.ForeignKey("photocard.PhotoCard", on_delete=models.CASCADE, verbose_name="포토카드")
    price = models.PositiveIntegerField(verbose_name="가격")
    fee = models.PositiveIntegerField(verbose_name="수수료")
    status = EnumField(PhotoCardSaleStatus, max_length=20, default=PhotoCardSaleStatus.SALE, blank=False)
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        verbose_name="구매자",
        related_name="bought_sales",
    )
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=False, verbose_name="판매자", related_name="sold_sales"
    )
    sold_at = models.DateTimeField(null=True, verbose_name="거래 완료 일시")

    class Meta:
        db_table = "photo_card_sale"
        verbose_name = "포토 카드 판매"
        indexes = [BrinIndex(fields=["updated_at"])]

    @property
    def key(self):
        return f"photo_card_sale_{self.uuid}"

    @property
    def total_price(self):
        return self.price + self.fee


class PhotoCardSaleHistory(models.Model):
    photo_card_sale = models.ForeignKey(
        "photocard.PhotoCardSale", on_delete=models.CASCADE, verbose_name="포토 카드 판매"
    )
    before = models.JSONField(verbose_name="수정 전")
    after = models.JSONField(verbose_name="수정 후")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "photo_card_sale_history"
        verbose_name = "포토 카드 판매 수정 이력"
        indexes = [BrinIndex(fields=["created_at"])]
