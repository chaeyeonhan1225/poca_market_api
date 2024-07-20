from celery import shared_task

from order.models import UserCash


@shared_task
def create_welcome_cash(user_id: int):
    from user.models import User

    user = User.objects.get(id=user_id)
    UserCash.objects.create(user=user, cash=10000)
