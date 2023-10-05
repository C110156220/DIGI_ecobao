from rest_framework import serializers
from .models import *

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

class Member_TokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['uid'] = get_id(user.account)
        token['account'] = user.account

        return token

class Data_Member_Serializers(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = "__all__"
        read_only_fields = ['uid']

class Data_MemberP_Serializers(serializers.ModelSerializer):
    class Meta:
        model = MemberP
        fields = "__all__"
        read_only_fields = ['uid','account']

class Data_pass_Serializers(serializers.ModelSerializer):
    class Meta:
        model = MemberP
        fields = ['account','password']
        read_only_fields = ['account','password']


def get_id(account):
    from .models import MemberP
    data = MemberP.objects.filter(account = account)
    print(data)
    try:
        if data[0].uid == None or data[0].uid == "" :
            return "notfound"
        else:
            return data[0].uid
    except Exception as e:
        print(e)
        return ""

class LoginSerializers(serializers.Serializer):
    account = serializers.CharField()
    password = serializers.CharField()

class StoreSerializers(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = "__all__"
