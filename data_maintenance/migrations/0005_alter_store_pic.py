# Generated by Django 4.1.10 on 2023-10-18 07:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_maintenance', '0004_store_city'),
    ]

    operations = [
        migrations.AlterField(
            model_name='store',
            name='pic',
            field=models.ImageField(null=True, upload_to='Store', verbose_name='店家照片'),
        ),
    ]
