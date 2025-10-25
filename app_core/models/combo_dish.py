from django.db import models
from django.core.validators import MinValueValidator

from app_core.models.dish import Dish
from app_core.models.combo import Combo

class ComboDish(models.Model):
    class Meta:
        db_table = "combo_dishes"

    id = models.AutoField(primary_key=True)
    combo = models.ForeignKey(Combo, on_delete=models.CASCADE, related_name="combo_dishes")
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE, related_name="combo_dishes")
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, default=None)