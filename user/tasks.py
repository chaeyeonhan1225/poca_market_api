import logging

from celery import shared_task

from order.models import UserCash

logger = logging.getLogger("poca_market_api")


@shared_task
def create_welcome_cash(user_id: int):
    from user.models import User

    welcome_cash = 10000
    user = User.objects.get(id=user_id)
    UserCash.objects.create(user=user, cash=welcome_cash)
    logger.info(f"welcome cash user.id={user.id}, cash={welcome_cash}")
