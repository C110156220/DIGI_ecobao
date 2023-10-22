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
    def change(self, request):
        """更新訂單"""
        try:
            oid = request.data.get('oid','')
            if oid == "": return(Response())
            order = Order.objects.get(oid=oid)
            serializer = OrderSerializer(order, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request):
        try:
            uid = request.user.uid
            oid = request.data.get('oid','')
            if uid == "" or oid == '':
                return(Response(status=status.HTTP_400_BAD_REQUEST,data="匹配失效"))
            order = Order.objects.get(oid = oid , uid_id = uid )
            order.delete()
            return Response(status=status.HTTP_200_OK,data="success")
        except Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND,data="沒資料")

    @action(detail=False, methods=['post'],permission_classes=[IsAuthenticated])
    def add(self,request):
        from django.utils import timezone
        from django.db import transaction
        try:
            with transaction.atomic():
                # 获取购物车数据
                import json
                data_list = request.data.get('cart_list',[]) ; print(data_list)
                # data_list = json.loads(request.data.get('cart_list','[]'))
                cart_items = Cart.objects.filter(cart_id__in=data_list)
                # cart_items = Cart.objects.select_related('gid__sid').filter(cart_id=data_list)
                if cart_items.count() == 0:
                    return(Response(status=404,data="購物車未匹配任何資料"))
                # 计算订单总额
                total = 0
                for cart_item in cart_items:
                    total += int(cart_item.price) * cart_item.quantity
                if Member.objects.filter(uid = request.user.uid).count() != 1:
                    return(Response(status=400,data="人?"))
                oid = "OD{0:06d}".format(Order.objects.all().count()+12)
                # 创建订单
                order_data = {
                    'oid': oid,
                    'uid': request.user.uid,  # 假设购物车数据与订单关联的用户是相同的
                    'order_time': timezone.now(),  # 你需要提供订单时间
                    'complete_time': None,  # 订单完成时间初始化为None，你需要在订单完成时更新它
                    'total': str(total),  # 将总额设置为购物车商品价格的总和
                    'status': '待接收'  # 订单初始状态
                }
                print(order_data['oid'])
                order_serializer = OrderSerializer(data=order_data)
                if order_serializer.is_valid():
                    order_serializer.save()
                else:
                    return Response(order_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                from goods.serializers import Goods_serializers
                # 创建订单详细记录
                for cart_item in cart_items:

                    try:
                        # print(cart_item.gid_id)
                        product = Goods.objects.get(gid=cart_item.gid_id)  # 假设产品有一个id字段
                        product_serializer = Goods_serializers(product)
                        product_price = product_serializer.data['price']
                    except Goods.DoesNotExist:
                        return Response("产品不存在", status=status.HTTP_404_NOT_FOUND)

                    order_food_data = {
                        'oid': order_serializer.data['oid'],
                        'gid': cart_item.gid_id,
                        'quantity': cart_item.quantity,
                        'discount': 0,
                        'subtotal': int(product_price) * cart_item.quantity
                    }

                    order_food_serializer = OrderFoodSerializer(data=order_food_data)
                    if order_food_serializer.is_valid():
                        order_food_serializer.save()
                    else:
                        return Response(order_food_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                # 创建订单支付方式（示例中为信用卡）
                order_payment_data = {
                    'oid': order_serializer.data['oid'],
                    'method': request.data.get('payment_method',None),
                    'credit_number': request.data.get('credit_num',None),
                    'credit_private': request.data.get('credit_private',None),
                    'credit_date_year': request.data.get('credit_date_year',None),
                    'credit_date_month': request.data.get('credit_date_month',None)
                }

                order_payment_serializer = OrderPaymentSerializer(data=order_payment_data)
                if order_payment_serializer.is_valid():
                    order_payment_serializer.save()
                else:
                    return Response(order_payment_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                # 删除购物车数据
                cart_items.delete()
                return Response("订单创建成功并购物车数据已删除", status=status.HTTP_201_CREATED)

        except Exception as e:
            # 处理错误，例如记录日志或发送通知
            return Response(f"发生错误：{e}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class CartViewset(viewsets.ModelViewSet):
    """購物車"""
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
            if Cart.objects.get(gid_id=gid,uid_id=uid):
                Cart_data = Cart.objects.get(gid_id=gid,uid_id=uid)
                Cart_data.quantity = str(quantity)
                Cart_data.save()
                return Response(status=status.HTTP_202_ACCEPTED,data="已存在，購物車數量變動!")
        except Cart.DoesNotExist:
            try:
                cart_id = "CT{0:05d}".format(Cart.objects.all().count()+12)
                if Cart.objects.filter(cart_id=cart_id).count() == 1:
                    import random
                    cart_id = "CT{0:05d}".format(Cart.objects.all().count()+random.randint(13,30))
                new_ob = Cart.objects.create(
                    cart_id = cart_id,
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
                return("請洽管理")

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
    @action(methods=['post'],detail=False,permission_classes=[IsAuthenticated])
    def delete(self,request):
        uid = request.user.uid ; cart_id = request.data.get('cart_id','')
        try:
            cart = Cart.objects.filter(uid_id=uid, cart_id=cart_id)
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
        ob = Cart.objects.select_related('gid__sid').filter(uid_id=uid)
        serializer = Cart_serializer(ob,many=True)
        return(Response(status=200,data=serializer.data))

    @action(methods=['get'],detail=False,permission_classes=[IsAuthenticated])
    def getid(self,request):
        import json
        uid = request.user.uid
        if MemberP.objects.filter(uid=uid).count() != 1:
            return(Response(status=404,data="未知帳號"))
        # begin!
        data_list = json.loads(request.data.get('data_list', '[]'))
        ob = Cart.objects.select_related('gid__sid').filter(cart_id=data_list)
        serializer = Cart_serializer(ob,many=True)
        return(Response(status=200,data=serializer.data))
