import uuid
from enum import unique

from django.conf import settings
from django.db import models
from enumfields import Enum, EnumField

from common.models import TimeRecordingMixin
from photocard.models import PhotoCard, PhotoCardSale


class Order(TimeRecordingMixin):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    payment = models.ForeignKey("order.Payment", on_delete=models.CASCADE)

    class Meta:
        db_table = "order"
        verbose_name = "주문 내역"


"""
실제로 구매한 포토카드
구매 당시의 price, fee는 snapshot으로 기록해놓는다.
"""


class OrderItem(TimeRecordingMixin):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    photo_card_sale = models.ForeignKey("photocard.PhotoCardSale", on_delete=models.CASCADE)
    price = models.PositiveIntegerField(verbose_name="판매가")
    fee = models.PositiveIntegerField(verbose_name="수수료")

    class Meta:
        db_table = "order_item"
        verbose_name = "주문 아이템"


@unique
class PaymentMethod(Enum):
    CASH = "CASH"

    class Labels:
        CASH = "현금"


@unique
class PaymentStatus(Enum):
    COMPLETED = "COMPLETED"

    class Labels:
        COMPLETED = "완료"


class Payment(TimeRecordingMixin):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    method = EnumField(PaymentMethod, default=PaymentMethod.CASH, max_length=20, blank=False, verbose_name="결제 수단")
    amount = models.DecimalField(max_digits=16, decimal_places=2, verbose_name="결제 금액")
    status = EnumField(PaymentStatus, max_length=20, default=PaymentStatus.COMPLETED, verbose_name="결제 상태")

    class Meta:
        db_table = "payment"
        verbose_name = "결제"


class UserCash(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    cash = models.IntegerField(blank=False, verbose_name="사용 현금")
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, null=True, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "user_cash"
        verbose_name = "유저 보유 캐시"
