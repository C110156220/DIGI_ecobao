
from rest_framework import serializers
from .models import *

class Goods_serializers(serializers.Serializer):
    class Meta:
        Model = Goods
        fields = "__all__"

class Evaluate_serializers(serializers.Serializer):
    class Meta:
        Model = Evaluate
        fields = "__all__"