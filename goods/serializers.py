
from rest_framework import serializers
from .models import *

class Goods_serializers(serializers.ModelSerializer):
    class Meta:
        model = Goods
        fields = "__all__"

class Goods_input_serializers(serializers.Serializer):
    type = serializers.CharField()
    name = serializers.CharField()
    quantity = serializers.IntegerField()
    food_pic = serializers.ImageField()
    price = serializers.IntegerField()
    ingredient = serializers.CharField()
    allergen = serializers.CharField()

class Evaluate_serializers(serializers.ModelSerializer):
    class Meta:
        model = Evaluate
        fields = ['evaid','star','explain']