from rest_framework import serializers

from app_core.models.order import Order, OrderStatus
from app_core.models.order_item import OrderItem, OrderItemType
from app_core.models.dining_table import DiningTable
from app_core.models.dish import Dish, DishStatus
from app_core.models.combo import Combo

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = "__all__"

class OrderSerializer(serializers.ModelSerializer):
    order_items = serializers.SerializerMethodField()

    def get_order_items(self, obj):
        return OrderItemSerializer(obj.order_items.filter(deleted_at=None), many=True).data

    class Meta:
        model = Order
        fields = "__all__"

class CreateOrderItemSerializer(serializers.Serializer):
    order = serializers.PrimaryKeyRelatedField(queryset=Order.objects.filter(status=OrderStatus.PENDING), required=True)
    type = serializers.ChoiceField(choices=OrderItemType.choices, required=True)
    dish = serializers.PrimaryKeyRelatedField(queryset=Dish.objects.filter(deleted_at=None, status=DishStatus.SELLING), required=False)
    combo = serializers.PrimaryKeyRelatedField(queryset=Combo.objects.filter(deleted_at=None), required=False)
    quantity = serializers.IntegerField(required=True, min_value=1)

    def __init__(self, *args, **kwargs):
        existing = set(self.fields.keys())
        fields = kwargs.pop("fields", []) or existing
        exclude = kwargs.pop("exclude", [])
        
        super().__init__(*args, **kwargs)
        
        for field in exclude + list(set(existing) - set(fields)):
            self.fields.pop(field, None)

    def validate(self, value):
        if value["type"] == OrderItemType.DISH and not value["dish"]:
            raise serializers.ValidationError("Dish is required")
        if value["type"] == OrderItemType.COMBO and not value["combo"]:
            raise serializers.ValidationError("Combo is required")
        return value

class UpdateOrderItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(required=False, min_value=1)

class CreateOrderSerializer(serializers.Serializer):
    customer_name = serializers.CharField(required=True)
    customer_phone = serializers.CharField(required=True)
    dining_table = serializers.PrimaryKeyRelatedField(queryset=DiningTable.objects.filter(deleted_at=None), required=True)
    order_items = CreateOrderItemSerializer(many=True, required=True, allow_empty=True, exclude=["order"])

class UpdateOrderSerializer(serializers.Serializer):
    customer_name = serializers.CharField(required=False)
    customer_phone = serializers.CharField(required=False)