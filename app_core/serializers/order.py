from rest_framework import serializers

from app_core.models.order import Order, OrderStatus
from app_core.models.order_item import OrderItem, OrderItemType

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = "__all__"

class CreateOrderItemSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=OrderItemType.choices, required=True)
    dish = serializers.IntegerField(required=False)
    combo = serializers.IntegerField(required=False)
    quantity = serializers.IntegerField(required=True, min_value=1)

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
    dining_table = serializers.IntegerField(required=True)
    order_items = CreateOrderItemSerializer(many=True, required=True, allow_empty=True)

class UpdateOrderSerializer(serializers.Serializer):
    customer_name = serializers.CharField(required=False)
    customer_phone = serializers.CharField(required=False)
    dining_table = serializers.IntegerField(required=False)