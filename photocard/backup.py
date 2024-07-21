# Generated by Django 5.0.7 on 2024-07-19 18:34
import os

from django.conf import settings
from django.db import migrations
from django.core.files.uploadedfile import SimpleUploadedFile


def create_default_photo_cards(apps, schema_editor):
    db = schema_editor.connection.alias
    photo_card = apps.get_model(app_label="photocard", model_name="PhotoCard")

    files = os.listdir(os.path.join(settings.BASE_DIR, "test_images"))
    for idx, file in enumerate(files):
        with open(os.path.join(settings.BASE_DIR, "test_images", file), "rb") as img:
            local_image = SimpleUploadedFile(file, content=img.read(), content_type="image/jpeg")
            if local_image:
                photo_card.objects.using(db).create(
                    image=local_image,
                    artist=f"Artist_{idx}",
                    title=file,
                )


def reverse_photo_cards(apps, schema_editor):
    db = schema_editor.connection.alias
    photo_card = apps.get_model(app_label="photocard", model_name="PhotoCard")

    photo_card.objects.using(db).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("photocard", "0001_initial"),
    ]

    operations = [migrations.RunPython(code=create_default_photo_cards, reverse_code=reverse_photo_cards)]
