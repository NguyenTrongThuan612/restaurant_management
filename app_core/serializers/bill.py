from rest_framework import serializers
from app_core.models.bill import Bill
from app_core.models.order import Order, OrderStatus
from app_core.models.user import User, UserStatus

class BillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bill
        fields = '__all__'

class CreateBillSerializer(serializers.Serializer):
    order = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all(), required=True)