from rest_framework.renderers import JSONRenderer
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action,permission_classes
from rest_framework.permissions import AllowAny,IsAuthenticated
# 回應
from django.http import HttpResponse

# 內部設計
from .models import Goods
from .serializers import *
# 取     得
from data_maintenance.models import Member


class res():
    """
    快速輸出
    """
    def __init__(self) -> None:
        from rest_framework.response import Response
        self.Response = Response
    def dataError(self):
        """前端給予的資料有誤"""
        return self.Response(
            status = 404,
            data = {
                'Error':'your data didnt match any data from database '
            }
        )
    def NotFound(self):
        """資料有誤"""
        return(self.Response(
            status=404,
            data={
                'Error':'Not Found,Please check your data correctly!'
            }
            ))

    def Success(self):
        """資料成功"""
        return(self.Response(
            status=200,
            data={
               'message':'success'
            }
        ))

    def output_data(self,dict):
        return(self.Response(
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
    serializer_class = Goods_serializers

    @action(methods=['get'],detail=False,permission_classes=[AllowAny])
    def store(self,request):
        sid = request.GET.get('sid','')
        if sid == '' :
            return res().NotFound()
        db_ob = Goods.objects.filter(sid_id = sid)
        if db_ob.count() == 0 :
           return res().dataError()
        serializer = Goods_serializers(db_ob,many=True)
        return(Response(status=200,data=serializer.data))

    @action(methods=['Get'],detail=False,permission_classes=[AllowAny])
    def all(self,request):
        """取得所有商品"""
        goods = Goods.objects.filter(status=1)
        serializer = Goods_serializers(goods,many=True)
        return(Response(status=200,data=serializer.data))

    @action(methods=['get'],detail=False,permission_classes=[AllowAny])
    def id(self,request):
        """取得該商品編號的商品"""
        gid = request.GET.get('gid','')
        if gid == '' :
            return (res().NotFound())
        db_ob = Goods.objects.filter(gid = gid)
        if db_ob.count() != 1 :
           return res().dataError()

        serializer = Goods_serializers(db_ob,many=True)
        return(Response(status=200,data=serializer.data))

    @action(methods=['GET'],detail=False,permission_classes=[IsAuthenticated])
    def allergen_avoid(self,request):
        import ast
        uid = request.user.uid
        if uid == '' : return res.NotFound()
        db_ob = Member.objects.filter(uid = uid)
        if db_ob.count() != 1 :
            return res().dataError()
        # 將字串轉為list
        print(ast.literal_eval(db_ob[0].allergen))
        return(res().output_data({"data":db_ob[0].allergen}))




class Goods_Upload_Viewsets(viewsets.ModelViewSet):
    """
    店家專用，上架商品、修改商品資訊
    """
    serializer_class = Goods_serializers
    @action(methods=['post'],detail=False,permission_classes=[IsAuthenticated|AllowAny])
    def upload(self,request):
        """上架商品"""
        uid = request.user.uid
        if Store.objects.filter(upid = uid).count() != 1:return(res().dataError())
        serializer = Goods_input_serializers(data = request.data)
        if serializer.is_valid():
            data = request.data
            ob = Goods.objects.create(
                gid = "G{0:05d}".format(Goods.objects.all().count() + 3),
                type = data['type'],
                sid = Store.object.get(upid = uid),
                name = data['name'],
                intro = data['intro'],
                quantity = data['quantity'],
                food_pic = data['food_pic'],
                price = data['price'],
                ingredient = data['ingredient'],
                allergen = data['allergen']
            )
            ob.save()
            return(res().Success())
        else:
            return(res().dataError())


    @action(methods=['post'],detail=False)
    def change(self,request):
        uid = request.user.uid
        if Store.objects.filter(upid = uid).count() != 1:return(res().dataError())
        serializer = Goods_input_serializers(data = request.data)
        if serializer.is_valid():
            pass
        else:
            return(res().dataError())

    @action(methods=['post'],detail=False,permission_classes=[IsAuthenticated])
    def delete(self,request):
        gid = request.data.get('gid','')
        if gid != '':
            if Goods.objects.filter(gid=gid).count() != 1 :
                return(Response(status=400,data="NotFound商品"))
        else:
           return(Response(status=400,data="商品編號未知"))
        ob = Goods.objects.get(gid=gid)
        ob.delete()
        return(Response(status=200,data="Success"))


class Evaluate_store_Viewset(viewsets.ModelViewSet):
    @action(methods=['POST'],detail=False,permission_classes=[IsAuthenticated])
    def new(self,request):
        sid =request.data.get('sid','')
        if Store.objects.filter(upid=sid).count() != 1:
            return(Response(status=404,data="未知餐廳"))
        evaid = "EV{0:05d}".format(Evaluate.objects.all().count() + 2)
        if Evaluate.objects.filter(evaid=evaid).count() == 1:
            evaid = "EV{0:05d}".format(Evaluate.objects.all().count() + 4)
        ob = Evaluate.objects.create(
            evaid = evaid,
            sid_id = sid,
            star = request.data.get('star',''),
            explain = request.data.get('explain','')
        )
        ob.save()
        return Response(status=200,data="success")

    @action(methods=['GET'],detail=False,permission_classes=[AllowAny])
    def store(self,request):
        sid = request.GET.get('sid','')
        if sid == '':
            return(Response(status=400,data="參數呢????"))
        if Store.objects.filter(sid = sid).count() != 1 :
            return(Response(status=400,data="餐聽notfound"))
        sid = Store.objects.get(sid=sid)
        data = Evaluate.objects.filter(sid_id = sid)
        serializer = Evaluate_serializers(data , many = True)
        return JSONResponse(serializer.data)

    @action(methods=['POST'],detail=False,permission_classes=[IsAuthenticated])
    def change(self,request):
        evaid = request.data.get('evaid','')
        if evaid == '': return(Response(status=400,data="評論?"))
        star = request.data.get('star','') ; explain = request.data.get('explain','')
        if star == '':
                return(Response(status=400,data="參數?"))
        data = Evaluate.objects.get(evaid = evaid)
        data.star = star
        data.explain = explain
        data.save()
        return Response(status=200,data="success")

    @action(methods=['POST'],detail=False,permission_classes=[IsAuthenticated])
    def delete(self,request):
        data = Evaluate.objects.get(evaid = request.data.get('evaid'))
        data.delete()
        return res().Success()

    @action(methods=['GET'],detail=False,permission_classes=[AllowAny])
    def score(self,request):
        sid = request.GET.get('sid','')
        if sid == '':
            return(res().dataError())
        
