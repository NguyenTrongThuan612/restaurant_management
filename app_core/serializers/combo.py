from rest_framework import serializers

from app_core.models.combo import Combo
from app_core.models.dish import Dish
from app_core.models.combo_dish import ComboDish
from app_core.serializers.dish import DishSerializer

class ComboDishSerializer(serializers.ModelSerializer):
    dish = DishSerializer(read_only=True)

    class Meta:
        model = ComboDish
        fields = "__all__"

class ComboSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    dishes = ComboDishSerializer(many=True, read_only=True)

    def get_image(self, obj):
        return obj.get_image()

    class Meta:
        model = Combo
        fields = "__all__"

class CreateComboSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    image = serializers.ImageField(required=True)
    discount = serializers.IntegerField(required=True, min_value=0)

class UpdateComboSerializer(serializers.Serializer):
    name = serializers.CharField(required=False)
    image = serializers.ImageField(required=False)
    discount = serializers.IntegerField(required=False, min_value=0)

class AddDishToComboSerializer(serializers.Serializer):
    dish = serializers.PrimaryKeyRelatedField(queryset=Dish.objects.filter(deleted_at=None))
    quantity = serializers.IntegerField(required=True, min_value=1)

class UpdateDishQuantityInComboSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(required=True, min_value=1)