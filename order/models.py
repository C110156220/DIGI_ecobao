from django.db import models
from .. data_maintenance.models import Member
# Create your models here.
class Cart(models.Model):
    cart_id = models.CharField('購物車編號',max_length=30,primary_key=True)
    uid = models.OneToOneField(
        Member,
        on_delete=models.CASCADE,
        primary_key=False,
        null=False,
    )
    gid = models.
    quantity = models.IntegerField('數量')