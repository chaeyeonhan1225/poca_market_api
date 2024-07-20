from django.conf import settings


def get_fee():
    return settings.PHOTO_CARD_SALE_POLICY["FEE"]
