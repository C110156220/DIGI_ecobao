# Generated by Django 4.1.10 on 2023-11-02 07:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_maintenance', '0007_member_prefer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='allergen',
            field=models.CharField(blank=True, max_length=500, verbose_name='過敏原'),
        ),
    ]