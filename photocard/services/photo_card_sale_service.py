import math
import uuid

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import transaction

from photocard.exceptions import ConflictException, UnauthorizedException
from photocard.models import PhotoCard, PhotoCardSale
from photocard.tasks import add_photo_card_sale_history
from photocard.utils import get_fee

User = get_user_model()


class PhotoCardSaleService:
    def __init__(self, photo_card: PhotoCard, seller: User):
        self.photo_card = photo_card
        self.seller = seller

    def __calculate_fee(self, price):
        return math.floor(price * get_fee())

    def create(self, price: int):
        fee = self.__calculate_fee(price)
        sale = PhotoCardSale(seller=self.seller, fee=fee, photo_card=self.photo_card, price=price)
        sale.save()
        return sale

    @transaction.atomic
    def __update_photo_card_sale(self, sale: PhotoCardSale, price: int):
        before_price = sale.price
        sale.price = price
        sale.fee = self.__calculate_fee(price)
        sale.save()
        transaction.on_commit(
            lambda: add_photo_card_sale_history.delay(
                sale_id=sale.id, before={"price": before_price}, after={"price": price}
            )
        )
        return sale

    def update_price(self, sale_id: uuid, price: int):
        photo_card_sale = PhotoCardSale.objects.get(uuid=sale_id)
        if photo_card_sale.seller != self.seller:
            raise UnauthorizedException(detail="수정 권한이 없습니다.")

        if cache.set(photo_card_sale.key, True, nx=True, timeout=60):
            try:
                return self.__update_photo_card_sale(photo_card_sale, price)
            finally:
                cache.delete(photo_card_sale.key)
        else:
            raise ConflictException(detail="거래가 진행중인 판매건입니다.")
