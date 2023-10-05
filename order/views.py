from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action,permission_classes
from rest_framework.status import *
from rest_framework.parsers import JSONParser
from django.contrib.auth.hashers import make_password,check_password
from itertools import chain
from .models import *
from ..data_maintenance.models import MemberP
class OrderViewset(viewsets.ModelViewSet):

    @action(methods=['get'],detail=False)
    def record(self,request):
        uid = request.user.uid
        if type(uid) != str :
            return(Response(status=500,data='Token Error，請洽管理'))
        data_order = Order.objects.get(uid = uid)
        data_all = 
        data_food = Order.objects.get('')

    @action(methods=['post'],detail=False)
    def send(self,request):
        pass

    @action(methods=['post'],detail=False)
    def send(self,request):
        pass

    @action(methods=['post'],detail=False)
    def send(self,request):
        pass


class CartViewset(viewsets.ModelViewSet):
    pass