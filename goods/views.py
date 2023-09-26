from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action,permission_classes
# 回應
from django.http import HttpResponse
from rest_framework.response import Response
# 內部設計
from .models import Goods
from .serializers import *
# 取     得
from ..data_maintenance.models import Member


class JSONResponse(HttpResponse):
    from rest_framework.parsers import JSONParser
    from rest_framework.renderers import JSONRenderer
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)

class Goods_Viewset(viewsets.ModelViewSet):

    @action(method=['Get'],detail=False)
    def all(self,request):
        data = Goods.objects.all()
        serializer = Goods_serializers(data,many=False)
        return JSONResponse(serializer.data)

    @action(method=['get'],detail=False)
    def id(self,request):
        data = Goods.objects.filter(gid = request.data.get('gid'))
        serializer = Goods_serializers(data,many=False)
        return JSONResponse(serializer.data)

    @action(method=['get'],detail=False)
    def type(self,request):
        form_type = request.data.get('type') ; form_name = request.data.get('name')
        if( form_type != None and form_name != None):
            data = Goods.objects.filter(
                type = form_type ,
                name = form_name
            )
            serializer = Goods_serializers(data,many=False)
            return JSONResponse(serializer.data)
        elif(form_type != None):
            data = Goods.objects.filter(
                type =form_type
            )
            serializer = Goods_serializers(data,many=False)
            return JSONResponse(serializer.data)
        elif(form_name != None):
            data = Goods.objects.filter(
                name = form_name
            )
            serializer = Goods_serializers(data,many=False)
            return JSONResponse(serializer.data)

    def allergen_avoid():
        data =
        return {
            'status':status,
            'data':data
        }

class Evaluate_store_Viewset(viewsets.ModelViewSet):
    @action(methods=['POST'],detail=False)
    def create(self,request):
        ob = Evaluate.objects.create(
            evaid = str(int(Evaluate.objects.all().count()) + 2),
            upid = request.data.get('upid'),
            star = request.data.get('star'),
            explain = request.data.get('intro')
        )
        ob.save()
        return Response(status=200,data="success")
    @action(methods=['GET'],detail=False)
    def store(self,request):
        data = Evaluate.objects.filter(evaid = request.data.get9('evaid'))
        serializer = Evaluate_serializers(data , many = True)
        return JSONResponse(serializer.data)
    @action(methods=['POST'],detail=False)
    def change(self,request):
        data = Evaluate.objects.filter(evaid = request.data.get('evaid'))
        data.star = request.data.get('star')
        data.explain = request.data.get('explain')
        data.save()
        return Response(status=200)
    @action(methods=['POST'],detail=False)
    def delete(self,request):
        data = Evaluate.objects.filter(evaid = request.data.get('evaid'))
        data.delete()
        return Response(status=200)

class Evaluate_goods_Viewset(viewsets.ModelViewSet):
    