import logging
import uuid

from celery import shared_task

from photocard.models import PhotoCardSaleHistory

logger = logging.getLogger("poca_market_api")


@shared_task
def add_photo_card_sale_history(sale_id: str, before: dict, after: dict):
    from photocard.models import PhotoCardSale

    photo_card_sale = PhotoCardSale.objects.filter(uuid=sale_id).first()
    if photo_card_sale:
        PhotoCardSaleHistory.objects.create(photo_card_sale=photo_card_sale, before=before, after=after)
    logger.info(f"photo card sale(uuid={sale_id}) history add")
