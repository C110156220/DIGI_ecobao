from rest_framework.renderers import JSONRenderer
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action,permission_classes
from rest_framework.permissions import AllowAny,IsAuthenticated
# 回應
from django.http import HttpResponse
# 合併輸出套件
from itertools import chain
# 內部
from .serializers import *
from .models import *
from ..data_maintenance.models import MemberP
from ..goods.views import res
class OrderViewset(viewsets.ModelViewSet):

    @action(methods=['get'],detail=False)
    def record(self,request):
        uid = request.user.uid
        if MemberP.objects.filter(uid = uid).count() != 1:
            return Response(status=404,data="未知帳號")
        ob = MemberP.objects.get(uid=uid)
        status = request.GET.get('status','')
        if  status != '':

            data_order = Order.objects.filter(uid_id = ob , status=status)
        else:
            data_order = Order.objects.filter(uid_id = ob)
            try:
                oid = list(data_order.oid_id)
                print(oid)
            except Exception as e:
                print(e)
                return(Response(status=500,data=e))

            # data_food = OrderFood.objects.filter(oid_id = record.oid for record in data_order)
            # data_payment = OrderPayment.objects.filter(oid_id = oid)


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
    serializer_class = Cart_serializers
    queryset=Cart.objects.all()

    @action(methods=['post'],detail=False,permission_classes=[IsAuthenticated])
    def add(self,request):
        # check member
        uid = request.user.uid
        if MemberP.objects.filter(uid=uid).count() != 1:
            return(Response(status=404,data="未知帳號"))
        # check  goods
        gid = request.data.get('gid','')
        if Goods.objects.filter(gid=gid).count() != 1:
            return(Response(status=404,data="未知商品"))
        # check params
        quantity = request.data.get('quantity','')
        # begin!
        import datetime
        current_time = datetime.datetime.now()
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        # 取得商品物件
        Goods_ob = Goods.objects.get(gid=gid)
        if int(Goods_ob[0].quantity)-quantity < 0 :
            return(Response(status=403,data={error:'商品數量不足！'}))
        # 新增購物車訊息
        try:
            new_ob = Cart.objects.create(
                Cart_id = "CT{0:05d}".format(Cart.objects.all().count()+3),
                quantity = quantity,
                gid_id=gid,
                price=Goods_ob[0].price,
                uid_id = uid,
                add_date=formatted_time
            )
            new_ob.save()
        except Exception as e:
            print(e)
            return(Response(status=404,data="資料有誤，無法儲存，請洽後端/{}".format(e)))

    @action(methods=['get'],detail=False,permission_classes=[IsAuthenticated])
    def get(self,request):
        uid = request.user.uid
        if MemberP.objects.filter(uid=uid).count() != 1:
            return(Response(status=404,data="未知帳號"))
        # begin!
        ob = Cart.objects.filter(uid_id=uid)
        serializer = Cart_serializers(ob,many=True)
        return(Response(status=200,data=serializer.data))
