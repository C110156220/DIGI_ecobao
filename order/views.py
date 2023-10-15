from rest_framework.renderers import JSONRenderer
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action,permission_classes
from rest_framework.permissions import AllowAny,IsAuthenticated
# 回應
from django.http import HttpResponse
from rest_framework import status
# 合併輸出套件
from itertools import chain
# 內部
from .serializers import *
from .models import *
from data_maintenance.models import MemberP
from goods.views import res
class OrderViewset(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    @action(methods=['get'],detail=False,permission_classes=[IsAuthenticated])
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
    @action(methods=['get'],detail=False,permission_classes=[IsAuthenticated])
    def update(self, request, pk=None):
        """更新訂單"""
        try:
            order = Order.objects.get(pk=pk)
            serializer = OrderSerializer(order, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    # 部分更新订单信息
    def partial_update(self, request, pk=None):
        return self.update(request, pk)

    def destroy(self, request, pk=None):
        try:
            order = Order.objects.get(pk=pk)
            order.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['POST'])
    def create_order_from_cart(self, request):
        cart_data = self.__get_cart_data(request.user.uid)  # 请替换成你的购物车数据获取逻辑
        if cart_data == "Account404":
            return(Response(status=status.HTTP_204_NO_CONTENT,data="帳號?"))
        elif cart_data == "Cart404":
            return(Response(status=status.HTTP_204_NO_CONTENT,data="未建立任何購物車資料"))
        else:
            # 构造订单数据，包括购物车中的商品信息
            order_data = {
                # 添加订单其他信息

                'quantity': cart_data['quantity'],
                'price': cart_data['price'],
                'foods': cart_data['']
            }

            serializer = OrderSerializer(data=order_data)
            if serializer.is_valid():
                serializer.save()
                # 在这里可以清空购物车或执行其他相关操作
                self.__clear_cart(request.user.uid)  # 请替换成你的购物车清空逻辑
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    # inner
    def __get_cart_data(self,uid):
        try:
            ob = Member.objects.get(uid=uid)
        except Member.DoesNotExist:
            return("Account404")
        try:
            ob = Cart.objects.filter(uid_id = ob)
        except Cart.DoesNotExist:
            return("Cart404")

        return ob
    def __clear_cart(self,uid):
        try:
            ob = Member.objects.get(uid=uid)
            ob = Cart.objects.filter(uid_id = ob)
            ob.delete()
            return None
        except Exception as e:
            return(Response(status=500,data="Error occur:{}".format(e)))



class CartViewset(viewsets.ModelViewSet):
    serializer_class = Cart_serializer
    queryset=Cart.objects.all()

    @action(methods=['post'],detail=False,permission_classes=[IsAuthenticated])
    def add(self,request):
        # check member
        uid = request.user.uid
        member = MemberP.objects.filter(uid=uid)
        if member.count() != 1:
            return(Response(status=404,data="未知帳號"))
        # check  goods
        try:
            gid = request.data.get('gid','')
            if Goods.objects.filter(gid=gid).count() != 1:
                return(Response(status=404,data="未知商品"))
        except Goods.DoesNotExist:
                return(Response(status=404,data="未知商品"))

        # check params
        quantity = request.data.get('quantity','')
        # begin!
        import datetime
        current_time = datetime.datetime.now()
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        # 取得商品檢查數量
        Goods_ob = Goods.objects.filter(gid=gid)
        if int(Goods_ob[0].quantity)-int(quantity) < 0 :
            return(Response(status=status.HTTP_400_BAD_REQUEST,data={'error':'商品數量不足！'}))
        try:
            if Cart.objects.filter(gid_id=gid,uid_id=uid).count() == 1:
                Cart_data = Cart.objects.get(gid_id=gid,uid_id=uid)
                Cart_data.quantity = str(quantity)
                Cart_data.save()
                return Response(status=status.HTTP_202_ACCEPTED,data="已存在，購物車數量變動!")
        except Cart.DoesNotExist:
            try:
                new_ob = Cart.objects.create(
                    cart_id = "CT{0:05d}".format(Cart.objects.all().count()+3),
                    quantity = quantity,
                    gid_id=gid,
                    price=Goods_ob[0].price,
                    uid_id = uid,
                    add_date=formatted_time
                )
                new_ob.save()
                return(Response(status=200,data="success"))
            except Exception as e:
                print(e)
                return(Response(status=404,data="資料有誤，無法儲存，請洽後端/{}".format(e)))

    @action(methods=['post'],detail=False,permission_classes=[IsAuthenticated])
    def change(self,request):
        uid = request.user.uid
        member = MemberP.objects.filter(uid=uid)
        if member.count() != 1:
            return(Response(status=404,data="未知帳號"))
        try:
            gid = request.data.get('gid','')
            if Goods.objects.filter(gid=gid).count() != 1:
                return(Response(status=404,data="未知商品"))
        except Goods.DoesNotExist:
                return(Response(status=404,data="未知商品"))
        try:
            Cart_data = Cart.objects.get(uid_id=uid,gid_id=gid)
            quantity= request.data.get('quantity','')
            if quantity == '': return(Response(status=400,data="數量?"))
            else:
                Cart_data.quantity= str(int(Cart_data.quantity) + int(quantity))
                Cart_data.save()
                return(Response(status=200,data="success"))
        except Cart.DoesNotExist:
            return(Response(status=404,data="未知購物車"))

    def delete(self,request):
        uid = request.data.get('uid','') ; gid = request.data.get('gid','')
        try:
            cart = Cart.objects.filter(uid_id=uid, gid_id=gid)
            if cart.exists():
                cart.delete()
                return(Response(status=200,data="success"))
            else:
                return(Response(status=404,data="購物車未知"))
        except Cart.DoesNotExist:
            return(Response(status=404,data="購物車未知"))

    @action(methods=['get'],detail=False,permission_classes=[IsAuthenticated])
    def get(self,request):
        uid = request.user.uid
        if MemberP.objects.filter(uid=uid).count() != 1:
            return(Response(status=404,data="未知帳號"))
        # begin!
        ob = Cart.objects.filter(uid_id=uid)
        serializer = Cart_serializer(ob,many=True)
        return(Response(status=200,data=serializer.data))
