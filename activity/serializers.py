
from rest_framework import serializers
from .models import *

class Activity_serializers(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = "__all__"
