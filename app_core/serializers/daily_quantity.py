from rest_framework import serializers
from datetime import date

from app_core.models.daily_quantity import DailyQuantity, DailyQuantityType
from app_core.models.dish import Dish
from app_core.models.combo import Combo
from app_core.serializers.dish import DishSerializer
from app_core.serializers.combo import ComboSerializer

class DailyQuantitySerializer(serializers.ModelSerializer):
    dish = DishSerializer(read_only=True)
    combo = ComboSerializer(read_only=True)

    class Meta:
        model = DailyQuantity
        fields = "__all__"

class CreateDailyQuantitySerializer(serializers.Serializer):
    date = serializers.DateField(required=True)
    type = serializers.ChoiceField(required=True, choices=DailyQuantityType.choices)
    dish = serializers.PrimaryKeyRelatedField(
        queryset=Dish.objects.filter(deleted_at=None),
        required=False,
        allow_null=True
    )
    combo = serializers.PrimaryKeyRelatedField(
        queryset=Combo.objects.filter(deleted_at=None),
        required=False,
        allow_null=True
    )
    quantity = serializers.IntegerField(required=True, min_value=0)

    def validate(self, data):
        dish = data.get('dish')
        combo = data.get('combo')
        quantity_type = data.get('type')

        if not dish and not combo:
            raise serializers.ValidationError("Either dish or combo must be provided.")

        if dish and combo:
            raise serializers.ValidationError("Cannot provide both dish and combo.")

        if quantity_type == DailyQuantityType.DISH and not dish:
            raise serializers.ValidationError("Dish is required when type is 'dish'.")

        if quantity_type == DailyQuantityType.COMBO and not combo:
            raise serializers.ValidationError("Combo is required when type is 'combo'.")

        return data

class UpdateDailyQuantitySerializer(serializers.Serializer):
    date = serializers.DateField(required=False)
    quantity = serializers.IntegerField(required=False, min_value=0)

