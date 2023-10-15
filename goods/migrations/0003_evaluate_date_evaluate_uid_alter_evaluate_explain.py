# Generated by Django 4.1.10 on 2023-10-13 17:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('data_maintenance', '0002_alter_store_pic'),
        ('goods', '0002_goods_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='evaluate',
            name='date',
            field=models.DateField(auto_now_add=True, null=True, verbose_name='填寫時間'),
        ),
        migrations.AddField(
            model_name='evaluate',
            name='uid',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='data_maintenance.member'),
        ),
        migrations.AlterField(
            model_name='evaluate',
            name='explain',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='心得或改進'),
        ),
    ]
