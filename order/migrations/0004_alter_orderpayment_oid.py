# Generated by Django 4.1.10 on 2023-10-25 05:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0003_alter_orderfood_oid_alter_orderpayment_oid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderpayment',
            name='oid',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orderpayments', to='order.order', unique=True),
        ),
    ]
