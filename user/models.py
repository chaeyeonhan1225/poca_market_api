from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.postgres.indexes import BrinIndex
from django.db import models, transaction
from django.db.models import Sum
from django.db.models.functions import Coalesce

from common.models import TimeRecordingMixin
from order.models import UserCash
from user.tasks import create_welcome_cash


class UserManager(BaseUserManager):

    @transaction.atomic
    def create_user(self, email, password=None, **extra_fields):
        if not email or not password:
            raise ValueError("이메일 또는 비밀번호가 유효하지 않습니다.")

        if User.objects.filter(email=email).exists():
            raise ValueError("중복되는 이메일입니다.")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)

        user.set_password(password)
        user.save(using=self._db)
        transaction.on_commit(lambda: create_welcome_cash.delay(user.id))
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, TimeRecordingMixin):
    email = models.EmailField(unique=True, verbose_name="이메일")
    nickname = models.CharField(max_length=50, unique=True, verbose_name="닉네임")

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nickname"]

    class Meta:
        db_table = "user"
        verbose_name = "유저"
        indexes = [BrinIndex(fields=["created_at"])]

    def __str__(self):
        return self.email

    @property
    def cash(self):
        return (
            UserCash.objects.filter(user=self)
            .only("user", "cash")
            .aggregate(sum=Coalesce(Sum("cash"), 0))
            .get("sum", 0)
        )
