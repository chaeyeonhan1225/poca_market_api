# Generated by Django 5.0.7 on 2024-07-19 18:14

import django.db.models.deletion
import enumfields.fields
import photocard.models
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="PhotoCard",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "image",
                    models.ImageField(
                        upload_to=photocard.models.upload_photo_card_to, verbose_name="포토카드 대표 이미지"
                    ),
                ),
                ("artist", models.CharField(max_length=20, verbose_name="아티스트")),
                ("title", models.CharField(max_length=150, verbose_name="포토카드 명")),
                (
                    "type",
                    enumfields.fields.EnumField(
                        default="앨범", enum=photocard.models.PhotoCardType, max_length=20, verbose_name="포토카드 타입"
                    ),
                ),
            ],
            options={
                "verbose_name": "포토카드",
                "db_table": "photo_card",
            },
        ),
        migrations.CreateModel(
            name="PhotoCardSale",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("uuid", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("price", models.PositiveIntegerField(verbose_name="가격")),
                ("fee", models.PositiveIntegerField(verbose_name="수수료")),
                (
                    "status",
                    enumfields.fields.EnumField(
                        default="판매중", enum=photocard.models.PhotoCardSaleStatus, max_length=20
                    ),
                ),
                ("sold_at", models.DateTimeField(null=True, verbose_name="거래 완료 일시")),
                (
                    "buyer",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="buyer",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="구매자",
                    ),
                ),
                (
                    "photo_card",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="photocard.photocard", verbose_name="포토카드"
                    ),
                ),
                (
                    "seller",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="seller",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="판매자",
                    ),
                ),
            ],
            options={
                "verbose_name": "포토 카드 판매",
                "db_table": "photo_card_sale",
            },
        ),
        migrations.CreateModel(
            name="PhotoCardSaleHistory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("before", models.JSONField()),
                ("after", models.JSONField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "photo_card_sale",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="photocard.photocardsale",
                        verbose_name="포토 카드 판매",
                    ),
                ),
            ],
            options={
                "verbose_name": "포토 카드 판매 수정 이력",
                "db_table": "photo_card_sale_history",
            },
        ),
    ]