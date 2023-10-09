
from rest_framework import serializers
from .models import *
class Cart_serializers(serializers.ModelSerializer):
    class Meta:
        Model = Cart
        fields = "__all__"

class Order_onlyid_serializers(serializers.ModelSerializer):
    class Meta:
        Model = Order
        fields = ['id']

class Order_data_serializers(serializers.ModelSerializer):
    class Meta:
        Model = Order
        fields = "__all__"
