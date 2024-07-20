from django.db import transaction

from order.exceptions import NotEnoughCashException
from order.models import Order, OrderItem, Payment, PaymentMethod, PaymentStatus, UserCash
from photocard.models import PhotoCardSale
from user.models import User


class OrderService:

    @transaction.atomic
    def create(self, buyer: User, sales: list[PhotoCardSale]):
        amount = sum([sale.total_price for sale in sales])
        if buyer.cash < amount:
            raise NotEnoughCashException("잔액이 부족합니다.")

        payment = Payment(user=buyer, method=PaymentMethod.CASH, amount=amount, status=PaymentStatus.COMPLETED)
        user_cash = UserCash(user=buyer, cash=(-amount), payment=payment)
        order = Order(user=buyer, payment=payment)
        items = [OrderItem(order=order, photo_card_sale=sale, price=sale.price, fee=sale.fee) for sale in sales]

        payment.save()
        user_cash.save()
        order.save()
        OrderItem.objects.bulk_create(items)

        return order
