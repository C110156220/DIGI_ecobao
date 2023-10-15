from django.db import models
from data_maintenance.models import Store,Member
# Create your models here.
class Goods(models.Model):
    gid = models.CharField("商品編號", max_length=30,primary_key=True)
    type = models.CharField("食物類型", max_length=30)
    sid = models.ForeignKey(Store, on_delete=models.CASCADE)
    name = models.CharField("商品名稱", max_length=30)
    intro = models.CharField("商品簡介", max_length=50, null=True)
    quantity = models.CharField("商品數量", default="1", null=False, max_length=10)
    food_pic = models.ImageField("商品照片", upload_to='assets/good', null=True)
    price = models.CharField("價格", default="50", null=False, max_length=10)
    ingredient = models.CharField("食物使用成分", max_length=200)
    allergen = models.CharField("過敏原成分", max_length=200)
    status = models.BooleanField('是否供應',default=True)

    def __str__(self):
        return "編號:{}，名稱:{}".format(self.gid,self.name)

    # USERNAME_FIELD = "gid"

class Evaluate(models.Model):
    evaid = models.CharField("留言編號",max_length=30,primary_key=True)
    sid = models.ForeignKey(Store, on_delete=models.CASCADE,null=True)
    uid = models.ForeignKey(Member, on_delete=models.CASCADE,null=True)
    star = models.IntegerField('分數')
    explain = models.CharField("心得或改進",max_length=100,blank=True,null=True)
    date = models.DateField('填寫時間',auto_now_add=True,null=True)

    def __str__(self):
        return "編號:{}，店家：{}，分數：{}".format(self.evaid,self.sid,self.star)
