from django.db import models
from data_maintenance.models import Member,Store
from goods.models import Goods,Evaluate
from goods.models import Goods

class Cart(models.Model):
    """購物車"""
    cart_id = models.CharField('購物車編號',max_length=30,primary_key=True)
    uid = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        primary_key=False,
        null=False,
    )
    gid = models.ForeignKey(Goods, verbose_name='商品編號', on_delete=models.CASCADE)
    quantity = models.IntegerField('購買數量')
    price = models.CharField('商品價格',max_length=10,default='0')
    add_date = models.DateTimeField('添加時間',auto_now=True)

class Order(models.Model):
    """訂單"""
    oid = models.CharField('訂單編號',max_length=50,primary_key=True)
    uid = models.ForeignKey( Member , verbose_name=("會員編號"), on_delete=models.CASCADE)
    order_time = models.DateTimeField(("訂購時間"), auto_now=False, auto_now_add=False)
    complete_time = models.DateTimeField(("完成時間"), auto_now=False, auto_now_add=False)
    total = models.CharField('訂單總額',max_length=50)
    status = models.CharField('訂單狀態',max_length=50)

class OrderFood(models.Model):
     """訂單詳細"""
     oid = models.ForeignKey(Order,on_delete=models.CASCADE, unique=False)
     gid = models.ForeignKey( Goods , verbose_name='商品編號', on_delete=models.CASCADE)
     quantity = models.IntegerField('餐點數量',null = False)
     discount = models.IntegerField('折扣',null=False)
     subtotal = models.IntegerField('小計',null=False)

class OrderPayment(models.Model):
    """付款方式"""
    oid = models.ForeignKey(Order,on_delete=models.CASCADE, unique=True)
    method = models.CharField('方法',null=False,max_length=50)
    credit_number = models.CharField('信用卡號碼',null=True,blank=False,max_length=50)
    credit_private = models.CharField('授權碼',null=True,blank=False,max_length=50)
    credit_date_year = models.DateField('期限年',null=True,blank=False,max_length=50)
    credit_date_month = models.DateField('期限月',null=True,blank=False,max_length=50)
