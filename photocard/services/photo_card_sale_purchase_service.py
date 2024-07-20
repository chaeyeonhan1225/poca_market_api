from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone

from order.service.order_service import OrderService
from photocard.exceptions import ConflictException, InvalidPurchaseException
from photocard.models import PhotoCardSale, PhotoCardSaleStatus

User = get_user_model()


class PhotoCardSalePurchaseService:
    def __init__(self, photo_card_sale: PhotoCardSale, buyer: User):
        self._photo_card_sale = photo_card_sale
        self.buyer = buyer

    def __validate_purchase(self):
        if self.buyer.id == self._photo_card_sale.seller_id:
            raise InvalidPurchaseException("본인과 거래할 수 없습니다.")

        if self._photo_card_sale.status != PhotoCardSaleStatus.SALE:
            raise InvalidPurchaseException("이미 판매된 포토카드입니다.")

    @transaction.atomic
    def __purchase(self) -> PhotoCardSale:  # TODO: 이름변경
        self._photo_card_sale.status = PhotoCardSaleStatus.COMPLETED
        self._photo_card_sale.buyer = self.buyer
        self._photo_card_sale.sold_at = timezone.now()
        OrderService().create(buyer=self.buyer, sales=[self._photo_card_sale])
        self._photo_card_sale.save()
        return self._photo_card_sale

    def purchase(self) -> PhotoCardSale:
        cache_key = self._photo_card_sale.key
        self.__validate_purchase()
        if cache.set(cache_key, True, nx=True, timeout=60):
            try:
                return self.__purchase()
            finally:
                cache.delete(cache_key)
        else:
            raise ConflictException(detail="거래 중인 판매건 입니다.")
