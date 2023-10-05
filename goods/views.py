from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action,permission_classes
# 回應
from django.http import HttpResponse

# 內部設計
from .models import Goods
from .serializers import *
# 取     得
from ..data_maintenance.models import Member


class res():
    """
    快速輸出
    """
    def __init__(self) -> None:
        from rest_framework.response import Response
        self.R = Response()
    def dataError(self):
        """前端給予的資料有誤"""
        return self.R(
            status = 404,
            data = {
                'Error':'your data didnt match any data from database '
            }
        )
    def NotFound(self):
        """資料有誤"""
        return(self.R(
            status=404,
            data={
                'Error':'Not Found,Please check your data correctly!'
            }
            ))

    def Success(self):
        """資料成功"""
        return(self.R(
            status=200,
            data={
               'message':'success'
            }
        ))

    def output_data(self,dict):
        return(self.R(
            status = 200 ,
            data = dict
        ))


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
    @action(methods=['get'],detail=False)
    def store(self,request):
        sid = request.GET.get('sid','')
        if sid == '' :
            return res.NotFound()
        db_ob = Goods.objects.filter(sid = sid)
        if db_ob.count() != 1 :
           return res.dataError()
        serializer = Goods_serializers(db_ob,many=False)
        return(res.output_data(serializer.data))

    @action(methods=['Get'],detail=False)
    def all(self,request):
        """取得所有商品"""
        data = Goods.objects.all()
        serializer = Goods_serializers(data,many=False)
        return JSONResponse(serializer.data)

    @action(method=['get'],detail=False)
    def id(self,request):
        """取得該商品編號的商品"""
        gid = request.GET.get('gid','')
        if gid == '' :
            return (res.NotFound())
        db_ob = Goods.objects.filter(gid = gid)
        if db_ob.count() != 1 :
           return res.dataError()
        serializer = Goods_serializers(db_ob,many=False)
        return(res.output_data(serializer.data))

    @action(method=['get'],detail=False) # 需重新撰寫
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

    def allergen_avoid(self,request):
        uid = request.data.get('uid','')
        if uid == '' : return res.NotFound()
        db_ob = Member.objects.filter(uid = uid)
        if db_ob.count() != 1 :
            return res.dataError()

        return(res().output_data({data:db_ob[0].allergen}))




class Goods_Upload_Viewsets(viewsets.ModelViewSet):
    @action(methods=['post'],detail=False)
    def upload(self,request):
        data1 = {}
        data1['sid'] = request.data.get('sid','')
        data1['type'] = request.data.get('type','')
        data1['name'] = request.data.get('name','')
        data1['intro'] = request.data.get('intro','')
        data1['price'] = request.data.get('price','')
        data1['ingredient'] = request.data.get('ingredient','')
        data1['allergen'] = request.data.get('allergen','')
        if self.check_null(data1):
            return Response(status=404,data='資料少給')

    @action(methods=['post'],detail=False)
    def change(self,request):
        pass
    @action(methods=['post'],detail=False)
    def delete(self,request):
        pass
    def check_null(self,dict):
        if '' in dict:
            if dict['sid'] == '':
                print('前端未給予店家編號')
                return True
            # if dict['']
        else:
            return False


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
        return res().Success()
