# Generated by Django 4.1.10 on 2023-10-13 17:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activity', '0004_alter_activity_pic1_alter_activity_pic2_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='pic1',
            field=models.ImageField(blank=True, null=True, upload_to='assets\\activity', verbose_name='首圖'),
        ),
        migrations.AlterField(
            model_name='activity',
            name='pic2',
            field=models.ImageField(blank=True, null=True, upload_to='assets\\activity', verbose_name='一張'),
        ),
        migrations.AlterField(
            model_name='activity',
            name='pic3',
            field=models.ImageField(blank=True, null=True, upload_to='assets\\activity', verbose_name='二張'),
        ),
        migrations.AlterField(
            model_name='activity',
            name='pic4',
            field=models.ImageField(blank=True, null=True, upload_to='assets\\activity', verbose_name='三張'),
        ),
    ]
