from django.db import models
from django.conf import settings

class DishStatus(models.TextChoices):
    SELLING = "selling"
    STOP_SELLING = "stop_selling"

class DishType(models.TextChoices):
    APPETIZER = "appetizer"
    MAIN_COURSE = "main_course"
    DESSERT = "dessert"
    DRINK = "drink"
    OTHER = "other"

class Dish(models.Model):
    class Meta:
        db_table = "dishes"

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to="dishes/", null=True, default=None)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=DishStatus.choices, default=DishStatus.SELLING)
    type = models.CharField(max_length=20, choices=DishType.choices, default=DishType.MAIN_COURSE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, default=None)

    def get_image(self):
        return f"{settings.APP_DOMAIN}{self.image.url}"