from django.db import models

# Create your models here.
class activity(models.Model):
    actid = models.CharField('活動編號',max_length=40,null=False,blank=False)
    title = models.CharField('活動標頭',max_length=100,null=False,blank=False)