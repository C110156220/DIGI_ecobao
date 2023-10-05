from django.db import models
from data_maintenance.models import Store
# Create your models here.
class Goods(models.Model):
    gid = models.CharField("商品編號",max_length=30 )
    type = models.CharField("食物類型",max_length=30)
    sid = models.ForeignKey(Store, on_delete=models.CASCADE)
    name = models.CharField("商品名稱",max_length=30)
    intro = models.CharField("商品簡介",max_length=50)
    food_pic = models.ImageField("商品照片")
    price = models.SmallIntegerField("價格")
    ingredient = models.CharField("食物使用成分",max_length=200)
    allergen = models.CharField("過敏原成分",max_length=200)

    def __str__(self):
        return "編號:{}，名稱:{}".format(self.gid,self.name)

    # USERNAME_FIELD = "gid"

class Evaluate(models.Model):
    evaid = models.CharField("留言編號",max_length=30,primary_key=True)
    gid = models.ForeignKey(Goods, on_delete=models.CASCADE)
    star = models.IntegerField('分數')
    explain = models.CharField("心得或改進",max_length=100,blank=True)

    def __str__(self):
        return "編號{},商品".format(self.gid)
