from django.db import models
# 會員MODEL
class Member(models.Model):

    uid = models.CharField("uid", max_length=50,primary_key=True)
    name = models.CharField("會員姓名",max_length=20)
    phone = models.CharField("電話",max_length=20)
    gender = models.CharField("性別",max_length=5)
    email = models.EmailField("電子信箱",max_length=50)
    address = models.CharField("通訊住址", max_length=50)
    birth = models.DateField("生日")
    allergen = models.CharField('過敏原',max_length=30,blank=True)
    # blank 是否菲必填
    USERNAME_FIELD = "uid"

    def __str__(self):
        return f"會員{self.name}您好"

from django.contrib.auth.models import AbstractBaseUser ,UserManager
class MemberP(AbstractBaseUser):
    username = None
    upid = models.OneToOneField(
        Member,
        on_delete=models.CASCADE,
        primary_key=True,
        null=False,
    )
    account = models.CharField("帳號", max_length=50 ,null=False,unique=True)
    password = models.CharField("密碼",max_length=100,null=False)
    is_verified = models.BooleanField(default=False)
    USERNAME_FIELD = "account"
    REQUIRED_FIELDS = ['password','username']
    objects = UserManager()
    @property
    def is_anonymous(self):
        return False

    def __str__(self):
        return f"會員{self.upid}您好"


# # 員工MODEL
class Employee(models.Model):
    eid = models.CharField("eid", max_length=50,primary_key=True)
    name = models.CharField("會員姓名",max_length=20)
    phone = models.CharField("電話",max_length=20)
    gender = models.CharField("性別",max_length=5)
    email = models.EmailField("電子信箱",max_length=50)
    address = models.CharField("通訊住址", max_length=50)
    birth = models.DateField("生日")
    USERNAME_FIELD = "eid"

class EmployeeP(models.Model):
    epid = models.OneToOneField(
        Employee,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    account = models.CharField("帳號", max_length=50)
    password = models.CharField("密碼",max_length=100)
    USERNAME_FIELD = "epid"
    REQUIRED_FIELDS = ['account', 'password']

class Store(models.Model):
    sid = models.CharField('商店編號',max_length=50)
    upid = models.OneToOneField(
        Member,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    type = models.CharField("食物類型",max_length=30)
    name = models.CharField("店家名稱", max_length=50)
    intro = models.CharField("店家簡介", max_length=50)
    area = models.CharField('所在區域',max_length=40)
    address = models.CharField("店家地址",max_length=50)
    lng = models.FloatField("經度")
    lat = models.FloatField("緯度")
    link = models.CharField("社群連結", max_length=50,null=True)
    on_business = models.BooleanField('是否營業')
    USERNAME_FIELD = "sid"

class Store_open(models.Model):
    stid = models.OneToOneField(
        Store,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    Mon_time_B = models.TimeField('周一開始',blank=True)
    Mon_time_N = models.TimeField('周一結束',blank=True)
    Tue_time_B = models.TimeField('周二開始',blank=True)
    Tue_time_N = models.TimeField('周二結束',blank=True)
    Wed_time_B = models.TimeField('周三開始',blank=True)
    Wed_time_N = models.TimeField('周三結束',blank=True)
    Thu_time_B = models.TimeField('周四開始',blank=True)
    Thu_time_N = models.TimeField('周四結束',blank=True)
    Fri_time_B = models.TimeField('周五開始',blank=True)
    Fri_time_N = models.TimeField('周五結束',blank=True)
    Sat_time_B = models.TimeField('周六開始',blank=True)
    Sat_time_N = models.TimeField('周六結束',blank=True)
    Sun_time_B = models.TimeField('周日開始',blank=True)
    Sun_time_N = models.TimeField('周日結束',blank=True)
    remark = models.CharField('備註',max_length=100,blank=True)
#     def __str__(self):
#         return f"工作人員{self.upid}您好"

# class EmployeeM(models.Model):
#     emid = models.OneToOneField(
#         Employee,
#         on_delete=models.CASCADE,
#         primary_key=True,
#     )
#     ename = models.CharField('緊急聯絡人姓名', max_length=50)
#     relation = models.CharField('關係', max_length=50)
#     phone = models.CharField('行動電話', max_length=50)
