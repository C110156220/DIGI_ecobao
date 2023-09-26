# Generated by Django 4.1.10 on 2023-09-21 14:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_maintenance', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='memberp',
            name='is_verified',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='memberp',
            name='account',
            field=models.CharField(max_length=50, unique=True, verbose_name='帳號'),
        ),
    ]
