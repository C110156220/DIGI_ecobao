# Generated by Django 4.1.10 on 2023-10-08 15:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('data_maintenance', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Goods',
            fields=[
                ('gid', models.CharField(max_length=30, primary_key=True, serialize=False, verbose_name='商品編號')),
                ('type', models.CharField(max_length=30, verbose_name='食物類型')),
                ('name', models.CharField(max_length=30, verbose_name='商品名稱')),
                ('intro', models.CharField(max_length=50, null=True, verbose_name='商品簡介')),
                ('quantity', models.CharField(default='1', max_length=10, verbose_name='商品數量')),
                ('food_pic', models.ImageField(null=True, upload_to='assets/good', verbose_name='商品照片')),
                ('price', models.CharField(default='50', max_length=10, verbose_name='價格')),
                ('ingredient', models.CharField(max_length=200, verbose_name='食物使用成分')),
                ('allergen', models.CharField(max_length=200, verbose_name='過敏原成分')),
                ('sid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data_maintenance.store')),
            ],
        ),
        migrations.CreateModel(
            name='Evaluate',
            fields=[
                ('evaid', models.CharField(max_length=30, primary_key=True, serialize=False, verbose_name='留言編號')),
                ('star', models.IntegerField(verbose_name='分數')),
                ('explain', models.CharField(blank=True, max_length=100, verbose_name='心得或改進')),
                ('sid', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='data_maintenance.store')),
            ],
        ),
    ]
