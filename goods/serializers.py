
from rest_framework import serializers
from .models import *

class Goods_serializers(serializers.ModelSerializer):
    class Meta:
        model = Goods
        fields = ['gid','type','name','intro','quantity','food_pic','price','ingredient','allergen']

class Goods_input_serializers(serializers.Serializer):
    type = serializers.CharField(source='data[type]')
    name = serializers.CharField(source='data[name]')
    quantity = serializers.CharField(source='data[quantity]')
    food_pic = serializers.ImageField(source='data[food_pic]')
    price = serializers.CharField(source='data[price]')
    ingredient = serializers.CharField(source='data[ingredient]')
    # allergen = serializers.CharField(source='data[allergen]')

class Evaluate_serializers(serializers.ModelSerializer):
    class Meta:
        model = Evaluate
        fields = ['evaid','star','explain']
