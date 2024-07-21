from django.db.models import Min
from enumfields.drf.serializers import EnumSupportSerializerMixin
from rest_framework import serializers

from photocard.models import PhotoCard, PhotoCardSale, PhotoCardSaleStatus
from user.serializers import SipmleUserSerializer


class PhotoCardSaleParamSerializer(EnumSupportSerializerMixin, serializers.Serializer):
    price = serializers.IntegerField(min_value=0)


class PhotoCardSaleSerializer(EnumSupportSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = PhotoCardSale
        fields = [
            "uuid",
            "photo_card_id",
            "fee",
            "price",
            "total_price",
            "status",
            "buyer_id",
            "seller_id",
        ]


class PhotoCardSerializer(EnumSupportSerializerMixin, serializers.ModelSerializer):
    image = serializers.ImageField(allow_null=False)

    class Meta:
        model = PhotoCard
        fields = ["id", "title", "artist", "image", "type"]


class PhotoCardDetailSerializer(EnumSupportSerializerMixin, serializers.ModelSerializer):
    completed_sales = PhotoCardSaleSerializer(read_only=True, many=True, source="to_completed_sales")
    min_price = serializers.SerializerMethodField()

    class Meta:
        model = PhotoCard
        fields = "__all__"

    def get_min_price(self, obj):
        return obj.photocardsale_set.filter(status=PhotoCardSaleStatus.SALE).aggregate(min=Min("price")).get("min")


class PhotoCardSaleDetailSerializer(EnumSupportSerializerMixin, serializers.ModelSerializer):
    buyer = SipmleUserSerializer(read_only=True)
    seller = SipmleUserSerializer(read_only=True)

    class Meta:
        model = PhotoCardSale
        fields = ["uuid", "photo_card", "price", "fee", "total_price", "status", "buyer", "seller"]
