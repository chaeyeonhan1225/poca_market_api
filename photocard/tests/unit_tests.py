from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase

from order.exceptions import NotEnoughCashException
from photocard.exceptions import InvalidPurchaseException, UnauthorizedException
from photocard.models import PhotoCard, PhotoCardSaleStatus
from photocard.scripts.init_photo_card_data import init_photo_card_data
from photocard.services.photo_card_sale_purchase_service import PhotoCardSalePurchaseService
from photocard.services.photo_card_sale_service import PhotoCardSaleService
from user.tasks import create_welcome_cash

User = get_user_model()


class PhotoCardUnitTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        init_photo_card_data()
        cls.userA = User.objects.create_user(email="tester1@example.com", nickname="김포카A", password="111111")
        cls.userB = User.objects.create_user(email="tester2@example.com", nickname="김포카B", password="123456")
        create_welcome_cash(user_id=cls.userA.id)
        create_welcome_cash(user_id=cls.userB.id)

    def test_판매건_등록(self):
        photo_card = PhotoCard.objects.all().first()
        sale = PhotoCardSaleService(photo_card=photo_card, seller=self.userA).create(price=10000)
        self.assertEqual(sale.photo_card_id, photo_card.id)
        self.assertEqual(sale.price, 10000)
        self.assertEqual(sale.status, PhotoCardSaleStatus.SALE)
        self.assertEqual(sale.fee, sale.price * settings.PHOTO_CARD_SALE_POLICY["FEE"])

    def test_판매건_가격_수정(self):
        photo_card = PhotoCard.objects.all().first()
        sale = PhotoCardSaleService(photo_card=photo_card, seller=self.userA).create(price=10000)
        self.assertEqual(sale.photo_card_id, photo_card.id)

        updated_sale = PhotoCardSaleService(photo_card=photo_card, seller=self.userA).update_price(
            sale_id=sale.uuid, price=20000
        )

        self.assertEqual(updated_sale.price, 20000)

    def test_포토카드_판매건_수정_실패_다른_유저의_판매건_수정(self):
        photo_card = PhotoCard.objects.all().first()
        sale = PhotoCardSaleService(photo_card=photo_card, seller=self.userA).create(price=10000)
        self.assertEqual(sale.photo_card_id, photo_card.id)

        with self.assertRaises(UnauthorizedException):
            PhotoCardSaleService(photo_card=photo_card, seller=self.userB).update_price(sale_id=sale.uuid, price=20000)

    def test_포토카드_구매(self):
        photo_card = PhotoCard.objects.all().first()
        sale = PhotoCardSaleService(photo_card=photo_card, seller=self.userA).create(price=500)

        result = PhotoCardSalePurchaseService(photo_card_sale=sale, buyer=self.userB).purchase()

        self.assertEqual(result.seller, self.userA)
        self.assertEqual(result.buyer, self.userB)
        self.assertEqual(result.status, PhotoCardSaleStatus.COMPLETED)
        self.assertEqual(self.userB.cash, 10000 - result.total_price)
        self.assertIsNotNone(result.sold_at)

    def test_포토카드_구매_실패_잘못된_요청(self):
        photo_card = PhotoCard.objects.all().first()
        sale = PhotoCardSaleService(photo_card=photo_card, seller=self.userA).create(price=5000)

        with self.assertRaises(InvalidPurchaseException):
            PhotoCardSalePurchaseService(photo_card_sale=sale, buyer=self.userA).purchase()

        PhotoCardSalePurchaseService(photo_card_sale=sale, buyer=self.userB).purchase()

        with self.assertRaises(InvalidPurchaseException):
            PhotoCardSalePurchaseService(photo_card_sale=sale, buyer=self.userB).purchase()

    def test_포토카드_구매_실패_잔액부족(self):
        photo_card = PhotoCard.objects.all().first()
        sale = PhotoCardSaleService(photo_card=photo_card, seller=self.userA).create(price=10000)

        with self.assertRaises(NotEnoughCashException):
            PhotoCardSalePurchaseService(photo_card_sale=sale, buyer=self.userB).purchase()

        self.assertEqual(self.userB.cash, 10000)
