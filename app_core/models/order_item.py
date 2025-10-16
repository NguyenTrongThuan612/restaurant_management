from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.db.models import Sum

from app_core.models.order import Order
from app_core.models.dish import Dish
from app_core.models.combo import Combo

class OrderItemType(models.TextChoices):
    DISH = "dish"
    COMBO = "combo"

class OrderItem(models.Model):
    class Meta:
        db_table = "order_items"

    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_items")
    type = models.CharField(max_length=20, choices=OrderItemType.choices)
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE, null=True, default=None, related_name="order_items")
    combo = models.ForeignKey(Combo, on_delete=models.CASCADE, null=True, default=None, related_name="order_items")
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    note = models.TextField(null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, default=None)

    def clean(self):
        if not self.dish and not self.combo:
            raise ValidationError("Either dish or combo must be set.")

        if self.dish and self.combo:
            raise ValidationError("Dish and combo cannot both be set.")

        if self.type == OrderItemType.DISH and not self.dish:
            raise ValidationError("OrderItem type 'dish' requires a dish.")

        if self.type == OrderItemType.COMBO and not self.combo:
            raise ValidationError("OrderItem type 'combo' requires a combo.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    @property
    def price(self):
        if self.type == OrderItemType.DISH:
            return self.dish.price
        elif self.type == OrderItemType.COMBO:
            return self.combo.dishes.aggregate(total_price=Sum('price'))['total_price'] - self.combo.discount