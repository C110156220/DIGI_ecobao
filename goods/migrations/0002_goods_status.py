# Generated by Django 4.1.10 on 2023-10-08 16:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='goods',
            name='status',
            field=models.BooleanField(default=True, verbose_name='是否供應'),
        ),
    ]