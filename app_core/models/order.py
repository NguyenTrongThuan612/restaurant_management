from django.db import models

from app_core.models.user import User
from app_core.models.dining_table import DiningTable

class OrderStatus(models.TextChoices):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Order(models.Model):
    class Meta:
        db_table = "orders"

    id = models.AutoField(primary_key=True)
    customer_name = models.CharField(max_length=255)
    customer_phone = models.CharField(max_length=15)
    dining_table = models.ForeignKey(DiningTable, on_delete=models.CASCADE, related_name="orders")
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    finished_at = models.DateTimeField(null=True, default=None)
    note = models.TextField(null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)