from celery import shared_task

from photocard.models import PhotoCardSaleHistory


@shared_task
def add_photo_card_sale_history(sale_id: int, before: dict, after: dict):
    from photocard.models import PhotoCardSale

    photo_card_sale = PhotoCardSale.objects.filter(id=sale_id).first()
    if photo_card_sale:
        PhotoCardSaleHistory.objects.create(photo_card_sale=photo_card_sale, before=before, after=after)
