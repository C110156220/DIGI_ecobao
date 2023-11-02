
from rest_framework import serializers
from .models import *

class Goods_serializers(serializers.ModelSerializer):
    class Meta:
        model = Goods
        fields = ['gid','type','name','intro','quantity','food_pic','price','ingredient','allergen','status']

class Goods_input_serializers(serializers.Serializer):
    type = serializers.CharField(source='data[type]')
    # name = serializers.CharField(source='data[name]')
    quantity = serializers.CharField(source='data[quantity]')
    # food_pic = serializers.ImageField(source='data[food_pic]')
    price = serializers.CharField(source='data[price]')
    ingredient = serializers.CharField(source='data[ingredient]')
    # allergen = serializers.CharField(source='data[allergen]')
    status = serializers.BooleanField(source='data[status]')

class Evaluate_serializers(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    class Meta:
        model = Evaluate
        fields = ['evaid','star','explain','date','uid_id','name']
    def get_name(self,data):
        try:
            return(data.uid.name)
        except Exception as e:
            print(e)
            return("遊客")
