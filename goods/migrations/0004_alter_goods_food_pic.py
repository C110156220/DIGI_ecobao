# Generated by Django 4.1.10 on 2023-11-01 14:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0003_evaluate_date_evaluate_uid_alter_evaluate_explain'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goods',
            name='food_pic',
            field=models.ImageField(null=True, upload_to='good', verbose_name='商品照片'),
        ),
    ]