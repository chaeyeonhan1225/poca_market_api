# Generated by Django 5.0.7 on 2024-07-20 16:14

import enumfields.fields
import order.models
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Order",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="생성 일시")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="수정 일시")),
                ("uuid", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
            ],
            options={
                "verbose_name": "주문 내역",
                "db_table": "order",
            },
        ),
        migrations.CreateModel(
            name="OrderItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="생성 일시")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="수정 일시")),
                ("price", models.PositiveIntegerField(verbose_name="판매가")),
                ("fee", models.PositiveIntegerField(verbose_name="수수료")),
            ],
            options={
                "verbose_name": "주문 아이템",
                "db_table": "order_item",
            },
        ),
        migrations.CreateModel(
            name="Payment",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="생성 일시")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="수정 일시")),
                ("uuid", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                (
                    "method",
                    enumfields.fields.EnumField(
                        default="CASH", enum=order.models.PaymentMethod, max_length=20, verbose_name="결제 수단"
                    ),
                ),
                ("amount", models.DecimalField(decimal_places=2, max_digits=16, verbose_name="결제 금액")),
                (
                    "status",
                    enumfields.fields.EnumField(
                        default="COMPLETED", enum=order.models.PaymentStatus, max_length=20, verbose_name="결제 상태"
                    ),
                ),
            ],
            options={
                "verbose_name": "결제",
                "db_table": "payment",
            },
        ),
        migrations.CreateModel(
            name="UserCash",
            fields=[
                ("uuid", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("cash", models.IntegerField(verbose_name="사용 현금")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "유저 보유 캐시",
                "db_table": "user_cash",
            },
        ),
    ]
