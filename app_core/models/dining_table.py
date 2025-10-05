from django.db import models

class DiningTable(models.Model):
    class Meta:
        db_table = "dining_tables"

    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=255)
    number_of_seats = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, default=None)