from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

from app_core.models.dish import Dish
from app_core.models.combo import Combo

class DailyQuantityType(models.TextChoices):
    DISH = "dish"
    COMBO = "combo"

class DailyQuantity(models.Model):
    class Meta:
        db_table = "daily_quantities"

    id = models.AutoField(primary_key=True)
    date = models.DateField()
    type = models.CharField(max_length=20, choices=DailyQuantityType.choices)
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE, null=True, default=None, related_name="daily_quantities")
    combo = models.ForeignKey(Combo, on_delete=models.CASCADE, null=True, default=None, related_name="daily_quantities")
    quantity = models.IntegerField(validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if not self.dish and not self.combo:
            raise ValidationError("Either dish or combo must be set.")

        if self.dish and self.combo:
            raise ValidationError("Dish and combo cannot both be set.")

        if self.type == DailyQuantityType.DISH and not self.dish:
            raise ValidationError("DailyQuantity type 'dish' requires a dish.")

        if self.type == DailyQuantityType.COMBO and not self.combo:
            raise ValidationError("DailyQuantity type 'combo' requires a combo.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

