from rest_framework import serializers

from app_core.models.dining_table import DiningTable

class DiningTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiningTable
        fields = "__all__"

class CreateDiningTableSerializer(serializers.Serializer):
    code = serializers.CharField(required=True)
    number_of_seats = serializers.IntegerField(required=True, min_value=1)

class UpdateDiningTableSerializer(serializers.Serializer):
    code = serializers.CharField(required=False)
    number_of_seats = serializers.IntegerField(required=False, min_value=1)
    
    def validate_code(self, value):
        if DiningTable.objects.filter(code=value, deleted_at=None).exists():
            raise serializers.ValidationError("Mã bàn ăn đã tồn tại!")
        return value