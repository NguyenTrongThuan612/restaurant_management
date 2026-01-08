from rest_framework import serializers
from datetime import date
from django.db.models import Sum

from app_core.models.dish import Dish, DishStatus, DishType
from app_core.models.order_item import OrderItem, OrderItemType
from app_core.models.order import Order, OrderStatus
from app_core.models.daily_quantity import DailyQuantity

class DishSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    sold_quantity_today = serializers.SerializerMethodField()
    remaining_quantity_today = serializers.SerializerMethodField()

    def get_image(self, obj):
        return obj.get_image()

    def get_sold_quantity_today(self, obj):
        """Tính số lượng món đã bán hôm nay"""
        today = date.today()
        sold_quantity = OrderItem.objects.filter(
            dish=obj,
            type=OrderItemType.DISH,
            deleted_at=None,
            order__created_at__date=today,
            order__status__in=[OrderStatus.PENDING, OrderStatus.COMPLETED]
        ).aggregate(total=Sum('quantity'))['total']
        return sold_quantity or 0

    def get_remaining_quantity_today(self, obj):
        """Tính số lượng món còn lại hôm nay"""
        today = date.today()
        # Lấy số lượng được set trong DailyQuantity
        daily_quantity = DailyQuantity.objects.filter(
            dish=obj,
            date=today
        ).first()
        
        if not daily_quantity:
            return None  # Chưa set số lượng cho hôm nay
        
        # Tính số lượng đã bán
        sold_quantity = self.get_sold_quantity_today(obj)
        
        # Số lượng còn lại = số lượng set - số lượng đã bán
        remaining = daily_quantity.quantity - sold_quantity
        return max(0, remaining)  # Đảm bảo không âm

    class Meta:
        model = Dish
        fields = "__all__"

class CreateDishSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    image = serializers.ImageField(required=True)
    price = serializers.DecimalField(required=True, max_digits=10, decimal_places=2)
    status = serializers.ChoiceField(required=True, choices=DishStatus.choices)
    type = serializers.ChoiceField(required=True, choices=DishType.choices)

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0")
        return value

class UpdateDishSerializer(serializers.Serializer):
    name = serializers.CharField(required=False)
    image = serializers.ImageField(required=False)
    price = serializers.DecimalField(required=False, max_digits=10, decimal_places=2)
    status = serializers.ChoiceField(required=False, choices=DishStatus.choices)
    type = serializers.ChoiceField(required=False, choices=DishType.choices)

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0")
        return value
        