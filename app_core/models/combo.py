from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings

from app_core.models.dish import Dish

class Combo(models.Model):
    class Meta:
        db_table = "combos"

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to="combos/", null=True, default=None)
    dishes = models.ManyToManyField(Dish, related_name="combos", through="ComboDish")
    discount = models.IntegerField(validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, default=None)

    def get_image(self):
        return f"{settings.APP_DOMAIN}{self.image.url}"