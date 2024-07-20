from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "password", "nickname"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "nickname", "last_login"]
        extra_kwargs = {"password": {"write_only": True}}


class SipmleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "nickname"]


class UserProfileSerializer(serializers.ModelSerializer):
    join_date = serializers.SerializerMethodField()
    sales_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "email", "nickname", "last_login", "join_date", "cash", "sales_count"]

    def get_join_date(self, obj):
        return obj.created_at.strftime("%Y-%m-%d")

    def get_sales_count(self, obj):  # 판매중, 판매완료 모두 포함
        return obj.sold_sales.count()
