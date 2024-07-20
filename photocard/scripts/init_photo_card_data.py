import os

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from photocard.models import PhotoCard


def init_photo_card_data():
    files = os.listdir(os.path.join(settings.BASE_DIR, "test_images"))

    photo_cards = []

    for idx, file in enumerate(files):
        with open(os.path.join(settings.BASE_DIR, "test_images", file), "rb") as img:
            local_image = SimpleUploadedFile(file, content=img.read(), content_type="image/jpeg")
            if local_image:
                photo_cards.append(
                    PhotoCard(
                        image=local_image,
                        artist=f"Artist_{idx}",
                        title=file,
                    )
                )

    PhotoCard.objects.bulk_create(photo_cards)
