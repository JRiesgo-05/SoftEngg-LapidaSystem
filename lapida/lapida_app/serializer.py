from rest_framework import serializers
from .models import FlowerShopItems


class FlowerShopItemsSerializer(serializers.ModelSerializer):
    # image = serializers.ImageField(validators=[])

    class Meta:
        model = FlowerShopItems
        fields = (
            "flower_name",
            "description",
            "price",
        )
