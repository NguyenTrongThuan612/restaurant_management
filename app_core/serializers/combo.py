from rest_framework import serializers
from datetime import date
from django.db.models import Sum

from app_core.models.combo import Combo
from app_core.models.dish import Dish
from app_core.models.combo_dish import ComboDish
from app_core.serializers.dish import DishSerializer
from app_core.models.order_item import OrderItem, OrderItemType
from app_core.models.order import Order, OrderStatus
from app_core.models.daily_quantity import DailyQuantity

class ComboDishSerializer(serializers.ModelSerializer):
    dish = DishSerializer(read_only=True)

    class Meta:
        model = ComboDish
        fields = "__all__"

class ComboSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    dishes = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    sold_quantity_today = serializers.SerializerMethodField()
    remaining_quantity_today = serializers.SerializerMethodField()

    def get_image(self, obj):
        return obj.get_image()

    def get_dishes(self, obj):
        return ComboDishSerializer(obj.combo_dishes, many=True).data

    def get_price(self, obj):
        return obj.price

    def get_sold_quantity_today(self, obj):
        """Tính số lượng combo đã bán hôm nay"""
        today = date.today()
        sold_quantity = OrderItem.objects.filter(
            combo=obj,
            type=OrderItemType.COMBO,
            deleted_at=None,
            order__created_at__date=today,
            order__status__in=[OrderStatus.PENDING, OrderStatus.COMPLETED]
        ).aggregate(total=Sum('quantity'))['total']
        return sold_quantity or 0

    def get_remaining_quantity_today(self, obj):
        """Tính số lượng combo còn lại hôm nay"""
        today = date.today()
        # Lấy số lượng được set trong DailyQuantity
        daily_quantity = DailyQuantity.objects.filter(
            combo=obj,
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