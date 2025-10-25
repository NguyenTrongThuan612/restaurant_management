from rest_framework import serializers
from app_core.models.bill import Bill
from app_core.models.order import Order
from app_core.serializers.user import UserSerializer

class BillSerializer(serializers.ModelSerializer):
    created_by = UserSerializer()

    class Meta:
        model = Bill
        fields = '__all__'

class CreateBillSerializer(serializers.Serializer):
    order = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all(), required=True)