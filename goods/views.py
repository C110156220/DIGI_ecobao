from rest_framework.renderers import JSONRenderer
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action,permission_classes,authentication_classes
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

    @action(methods=['get'],detail=False,permission_classes=[AllowAny],authentication_classes=[])
    def store(self,request):
        sid = request.GET.get('sid','')
        if sid == '' :
            return res().NotFound()
        if False :
            uid = request.user.uid
            Mem_allergen = Member.objects.get(uid=uid).allergen
            import json
            db_ob = Goods.objects.filter(sid_id = sid).exclude(allergen=json.loads(Mem_allergen))
            if db_ob.count() == 0 :
                return res().dataError()
            serializer = Goods_serializers(db_ob,many=True)
            return(Response(status=200,data=serializer.data))
        else:
            sid = Store.objects.get(sid=sid)
            db_ob = Goods.objects.filter(sid_id = sid)
            if db_ob.count() == 0 :
                return res().dataError()
        serializer = Goods_serializers(db_ob,many=True)
        return(Response(status=200,data=serializer.data))

    @action(methods=['Get'],detail=False,permission_classes=[AllowAny],authentication_classes=[])
    def all(self,request):
        """取得所有商品"""
        goods = Goods.objects.filter(status=1)
        serializer = Goods_serializers(goods,many=True)
        return(Response(status=200,data=serializer.data))

    @action(methods=['get'],detail=False,permission_classes=[AllowAny],authentication_classes=[])
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
    @authentication_classes([])
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
        print(uid)
        if Store.objects.filter(upid_id = uid).count() != 1:return(res().dataError())
        serializer = Goods_input_serializers(data = request.data)
        if serializer.is_valid():
            data = request.data
            if data['food_pic'] != None:
                pic = PicSave(data['food_pic'],'good')
                if pic == "base64 error" or pic == False:
                    return(Response(status=400,data="照片儲存失敗，請確認編碼"))
            else:
                pic = None
            try:
                ob = Goods.objects.create(
                    gid = "G{0:05d}".format(Goods.objects.all().count() + 3),
                    type = data['type'],
                    sid = Store.objects.get(upid = uid),
                    name = data['name'],
                    intro = data['intro'],
                    quantity = data['quantity'],
                    food_pic = pic,
                    price = data['price'],
                    ingredient = data['ingredient'],
                    allergen = data['allergen'],
                    status = data['status']
                )
                ob.save()
                return(res().Success())
            except Exception as e:
                print(e)
                return(Response(status=500))

        else:
            errors = serializer.errors
            print("建立失敗")
            print(errors)
            return(Response(status=400,data=errors))


    @action(methods=['post'],detail=False , permission_classes=[IsAuthenticated|AllowAny])
    def change(self,request):
        """編輯"""
        uid = request.user.uid
        print(uid)
        if Store.objects.filter(upid_id = uid).count() != 1:return(res().dataError())
        serializer = Goods_input_serializers(data = request.data)
        if serializer.is_valid():
            ob = Goods.objects.get(gid = request.data.get('gid',''))
            ob.type = request.data['type']
            ob.quantity = request.data['quantity']
            ob.price = request.data['price']
            ob.ingredient = request.data['ingredient']
            ob.save()
            return(Response(status=200,data="success"))
        else:
            return(res().dataError())

    @action(methods=['post'],detail=False,permission_classes=[IsAuthenticated])
    def delete(self,request):
        """刪除"""
        uid = request.user.uid
        gid = request.data.get('gid','')
        if gid != '':
            if Goods.objects.filter(gid=gid,sid_id = uid).count() != 1 :
                return(Response(status=400,data="NotFound商品"))
        else:
           return(Response(status=400,data="商品編號未知"))
        ob = Goods.objects.get(gid=gid)
        ob.delete()
        return(Response(status=200,data="Success"))
    @action(methods=['post'],detail=False,permission_classes=[IsAuthenticated])
    def unavailable(self,request):
        uid = request.user.uid
        print(uid)
        if Store.objects.filter(upid_id = uid).count() != 1:return(res().dataError())
        try:
            ob = Goods.objects.get(gid=request.data['gid'])
            ob.status = False
            ob.save()
        except Goods.DoesNotExist:
            return(Response(status=404,data="未知商品"))
        return(Response(status=200,data="success"))
    @action(methods=['post'],detail=False,permission_classes=[IsAuthenticated])
    def available(self,request):
        uid = request.user.uid
        print(uid)
        if Store.objects.filter(upid_id = uid).count() != 1:return(res().dataError())
        try:
            ob = Goods.objects.get(gid=request.data['gid'])
            ob.status = True
            ob.save()
        except Goods.DoesNotExist:
            return(Response(status=404,data="未知商品"))
        return(Response(status=200,data="success"))

class Evaluate_store_Viewset(viewsets.ModelViewSet):
    @action(methods=['POST'],detail=False,permission_classes=[IsAuthenticated])
    def new(self,request):
        from order.models import Order ; from order.serializers import Order_output_Serializer

        oid =request.data.get('oid','')
        if oid == '':
            return(Response(status=404,data="參數?"))
        try:
            ob = Order.objects.filter(oid = oid)
            ser = Order_output_Serializer(ob,many = True)
            sid = []
            for i in ser.data[0]['orderfoods']:
                sid.append(i['sid'])
            if len(set(sid)) == 1:
                ok = True
            else:
                ok = False
        except Order.DoesNotExist:
            return(Response(status=404,data="未與資料庫匹配"))
        except Exception as e :
            print(e)
            return(Response(status=500,data="系統出錯，請洽詢後端"))
        if ok:
            evaid = "EV{0:05d}".format(Evaluate.objects.all().count() + 2)
            if Evaluate.objects.filter(evaid=evaid).count() == 1:
                evaid = "EV{0:05d}".format(Evaluate.objects.all().count() + 4)

            ob = Evaluate.objects.create(
                evaid = evaid,
                sid = Store.objects.get(sid=sid[0]),
                star = request.data.get('star',''),
                explain = request.data.get('explain',''),
                uid_id = request.user.uid
            )
            ob.save()
            return Response(status=200,data="success")
        else:
            return(Response(status=400,data="訂單涵蓋多店家"))

    @action(methods=['GET'],detail=False,permission_classes=[AllowAny],authentication_classes=[])
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

    @authentication_classes([])
    @action(methods=['GET'],detail=False,permission_classes=[AllowAny],authentication_classes=[])
    def store_score(self,request):
        sid = request.GET.get('sid','')
        if sid == '':
            return(res().dataError())
        sid = Store.objects.get(sid=sid)
        from django.db.models import Sum
        import math
        total_score_for_sid = Evaluate.objects.filter(sid=sid).aggregate(total_score=Sum('star'))['total_score']/Evaluate.objects.filter(sid=sid).count()
        return(Response(status=200,data={'rating':math.floor(total_score_for_sid)}))


def PicSave(decodetext,target):
            from PIL import Image
            import base64,uuid,os
            from django.core.files.base import ContentFile
            from ecobao.settings import MEDIA_ROOT
            # 將Base64數據解碼
            try:
                image_data = base64.b64decode(decodetext.split(',')[1])
            except base64.binascii.Error:
                return("base64 error")
            # 創建文件對象
            try:
            # 在media目錄下創建一個唯一的文件名，或者使用您自己的文件命名邏輯
                file_name = str(uuid.uuid4())
                img_url = os.path.join(MEDIA_ROOT,'{}/{}.png'.format(target,file_name))
                # address = '/assets/{}/{}.png'.format(target,file_name)
                image_file = ContentFile(image_data,name="{}.png".format(file_name))
                # with open(img_url,'wb') as f:
                #     f.write(image_data)
                return image_file
            except Exception as e:
                print("Error in creating Image file -> {}".format(e))
                return False
            # 將文件保存到media目錄
            # try:
            #     img_PIL = Image.open(address)
            #     print(img_PIL)
            # except Exception as e:
            #     print(e)
            #     return False
