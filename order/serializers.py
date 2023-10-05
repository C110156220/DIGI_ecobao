
from rest_framework import serializers
from .models import *

class Order_onlyid_serializers(serializers.Serializer):
    class Meta:
        Model = Order
        fields = ['id']

class Order_data_serializers(serializers.Serializer):
    class Meta:
        Model = Order
        fields = "__all__"
