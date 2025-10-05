from rest_framework import serializers

from app_core.models.dish import Dish

class DishSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        return obj.get_image()

    class Meta:
        model = Dish
        fields = "__all__"

class CreateDishSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    image = serializers.ImageField(required=True)
    price = serializers.DecimalField(required=True, max_digits=10, decimal_places=2)

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0")
        return value

class UpdateDishSerializer(serializers.Serializer):
    name = serializers.CharField(required=False)
    image = serializers.ImageField(required=False)
    price = serializers.DecimalField(required=False, max_digits=10, decimal_places=2)

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0")
        return value
        