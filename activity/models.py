from django.db import models

class Activity(models.Model):
    actid = models.CharField('活動編號',max_length=40,null=False,blank=False)
    title = models.CharField('活動標頭',max_length=100,null=False,blank=True)
    author = models.CharField('作者',max_length=30)
    upload_date = models.DateField('發文時間',null=False)
    down_date = models.DateField('下架時間',null=False)
    content = models.CharField('活動內文',max_length=100000,null=False,blank=True)
    status = models.BooleanField("是否上架",default=True)
    pic1 = models.ImageField("首圖", upload_to="assets/activity/", null=True,blank=True)
    pic2 = models.ImageField("一張", upload_to="assets/activity/", null=True,blank=True)
    pic3 = models.ImageField("二張", upload_to="assets/activity/", null=True,blank=True)
    pic4 = models.ImageField("三張", upload_to="assets/activity/", null=True,blank=True)

    def __str__(self):
        return "{}，時間:{}".format(self.title,self.upload_date)
