# Generated by Django 5.0.7 on 2024-07-20 08:14

import enumfields.fields
import order.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("order", "0003_alter_payment_method_alter_payment_status"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="usercash",
            options={"verbose_name": "유저 보유 캐시"},
        ),
        migrations.AlterField(
            model_name="payment",
            name="method",
            field=enumfields.fields.EnumField(
                default="CASH", enum=order.models.PaymentMethod, max_length=20, verbose_name="결제 수단"
            ),
        ),
        migrations.AlterField(
            model_name="payment",
            name="status",
            field=enumfields.fields.EnumField(
                default="COMPLETED", enum=order.models.PaymentStatus, max_length=20, verbose_name="결제 상태"
            ),
        ),
    ]
