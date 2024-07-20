# Generated by Django 5.0.7 on 2024-07-20 08:06

import django.contrib.postgres.indexes
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("user", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="user",
            options={"verbose_name": "유저"},
        ),
        migrations.AlterField(
            model_name="user",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, verbose_name="생성 일시"),
        ),
        migrations.AlterField(
            model_name="user",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, verbose_name="수정 일시"),
        ),
        migrations.AddIndex(
            model_name="user",
            index=django.contrib.postgres.indexes.BrinIndex(fields=["created_at"], name="user_created_53e887_brin"),
        ),
        migrations.AlterModelTable(
            name="user",
            table="user",
        ),
    ]