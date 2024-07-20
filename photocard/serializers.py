from enumfields.drf.serializers import EnumSupportSerializerMixin
from rest_framework import serializers

from photocard.models import PhotoCard, PhotoCardSale
from user.serializers import SipmleUserSerializer


class PhotoCardSaleParamSerializer(EnumSupportSerializerMixin, serializers.Serializer):
    price = serializers.IntegerField(min_value=0)


class PhotoCardSaleSerializer(EnumSupportSerializerMixin, serializers.ModelSerializer):

    class Meta:
        model = PhotoCardSale
        fields = ["fee", "price", "total_price", "created_at", "updated_at", "status", "buyer", "seller"]


class PhotoCardSerializer(EnumSupportSerializerMixin, serializers.ModelSerializer):
    price = serializers.SerializerMethodField(allow_null=True)

    class Meta:
        model = PhotoCard
        fields = ["id", "title", "artist", "image", "type", "price"]
        read_only_fields = ["price"]

    def get_price(self, obj):
        return obj.min_price


class PhotoCardDetailSerializer(EnumSupportSerializerMixin, serializers.ModelSerializer):
    recent_sales = PhotoCardSaleSerializer(read_only=True, many=True, source="to_photocardsale")

    class Meta:
        model = PhotoCard
        fields = "__all__"


class PhotoCardSaleDetailSerializer(EnumSupportSerializerMixin, serializers.ModelSerializer):
    buyer = SipmleUserSerializer(read_only=True)
    seller = SipmleUserSerializer(read_only=True)

    class Meta:
        model = PhotoCardSale
        fields = ["uuid", "photo_card", "price", "fee", "total_price", "status", "buyer", "seller"]
