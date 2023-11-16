from rest_framework.renderers import JSONRenderer
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
# 回應
from django.http import HttpResponse
from rest_framework import status
# 合併輸出套件
from itertools import chain
# 內部
from .serializers import *
from .models import *
from data_maintenance.models import MemberP
from notice.app import Email


class Order_read_Viewset(viewsets.ModelViewSet):
    serializer_class = Order_output_Serializer

    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated])
    def all(self, request):
        uid = request.user.uid
        if Member.objects.filter(uid=uid).count() != 1:
            return Response(status=404, data="未知帳號")
        from django.shortcuts import get_object_or_404
        member = get_object_or_404(Member, uid=uid)

        # 查询该会员的订单信息
        orders = Order.objects.filter(uid=member).prefetch_related(
            'orderfoods', 'orderpayments')
        # 使用序列化器将订单数据序列化
        order_data = Order_output_Serializer(orders, many=True).data

        # 返回结果给前端
        if not order_data:  # 使用空列表作为条件判断
            return Response(status=202, data="會員未建立任何訂單紀錄")
        else:
            return Response(status=200, data=order_data)

    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated])
    def status(self, request):
        uid = request.user.uid
        if Member.objects.filter(uid=uid).count() != 1:
            return Response(status=404, data="未知帳號")
        if request.GET.get('status', '') == '':
            return Response(status=404, data="參數?")
        from django.shortcuts import get_object_or_404
        member = get_object_or_404(Member, uid=uid)
        orders = Order.objects.filter(uid=member, status=request.GET.get(
            'status')).prefetch_related('orderfoods', 'orderpayments')
        # 使用序列化器将订单数据序列化
        order_data = Order_output_Serializer(orders, many=True).data
        if not order_data:  # 使用空列表作为条件判断
            return Response(status=202, data="會員未建立任何訂單紀錄")
        else:
            return Response(status=200, data=order_data)


class OrderViewset(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated])
    def complete(self, request):
        try:
            oid = request.data.get('oid')
            if oid == None:
                return (Response(status=404, data="訂單?"))
            Order_ob = Order.objects.get(oid=oid)
            Order_ob.status = "已完成"
            Order_ob.save()
            serializer = OrderSerializer(Order_ob)
            print(serializer.data)

            return (Response(status=200, data="success"))
        except Order.DoesNotExist:
            return (Response(status=404, data="無訂單紀錄"))
        except Exception as e:
            return (Response(status=500, data="系統出錯，請洽後端，問題：{}".format(e)))

    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated])
    def cancel(self, request):
        try:
            oid = request.data.get('oid')
            if oid == None:
                return (Response(status=404, data="訂單?"))
            Order_ob = Order.objects.get(oid=oid)
            Order_ob.status = "已取消"
            Order_ob.save()
            OrderCancel(
                oid=oid,
                # type = request.data.get('type')
                msg=request.data.get('msg', '')
            ).save()
            return (Response(status=200, data="success"))
        except Order.DoesNotExist:
            return (Response(status=404, data="無訂單紀錄"))
        except Exception as e:
            return (Response(status=500, data="系統出錯，請洽後端，問題：{}".format(e)))

    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated])
    def food_already(self, request):
        try:
            oid = request.data.get('oid')
            if oid == None:
                return (Response(status=404, data="訂單?"))
            Order_ob = Order.objects.get(oid=oid)
            Order_ob.status = "未取餐"
            Order_ob.save()
            OrderCancel(
                oid=oid,
                # type = request.data.get('type')
                msg=request.data.get('msg', '')
            ).save()
            return (Response(status=200, data="success"))
        except Order.DoesNotExist:
            return (Response(status=404, data="無訂單紀錄"))
        except Exception as e:
            return (Response(status=500, data="系統出錯，請洽後端，問題：{}".format(e)))

    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated])
    def accept(self, request):
        uid = request.user.uid
        try:
            oid = request.data.get('oid')
            if oid == None:
                return (Response(status=404, data="訂單?"))
            Order_ob = Order.objects.get(oid=oid)
            Order_ob.status = "已接單"
            Order_ob.save()
            return (Response(status=200, data="success"))
        except Order.DoesNotExist:
            return (Response(status=404, data="無訂單紀錄"))
        except Exception as e:
            print(e)
            return (Response(status=500, data="系統出錯，請洽後端，問題：{}".format(e)))

    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated])
    def change(self, request):
        """更新訂單"""
        try:
            oid = request.data.get('oid', '')
            reason = request.data.get('reason', '')
            if oid == "":
                return (Response())
            order = Order.objects.get(oid=oid)
            serializer = OrderSerializer(order, data=request.data)
            order_cancel_seri = OrderCancel
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated])
    def delete(self, request):
        try:
            uid = request.user.uid
            oid = request.data.get('oid', '')
            if uid == "" or oid == '':
                return (Response(status=status.HTTP_400_BAD_REQUEST, data="匹配失效"))
            order = Order.objects.get(oid=oid, uid_id=uid)
            order.delete()
            return Response(status=status.HTTP_200_OK, data="success")
        except Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND, data="沒資料")

    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated])
    def notice(self, request):
        try:
            oid = request.data.get('oid')
            if oid == None:
                return (Response(status=404, data="訂單?"))
            Order_ob = Order.objects.get(oid=oid)
            Order_ob.status = "未取餐"
            Order_ob.save()
            return (Response(status=200, data="success"))
        except Order.DoesNotExist:
            return (Response(status=404, data="無訂單紀錄"))
        except Exception as e:
            print(e)
            return (Response(status=500, data="系統出錯，請洽後端，問題：{}".format(e)))

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def add(self, request):
        from django.utils import timezone
        from django.db import transaction
        try:
            with transaction.atomic():
                # 获取购物车数据
                import json
                data_list = request.data.get('cart_list', [])
                print(data_list)
                # data_list = json.loads(request.data.get('cart_list','[]'))
                cart_items = Cart.objects.filter(cart_id__in=data_list)
                # cart_items = Cart.objects.select_related('gid__sid').filter(cart_id=data_list)
                if cart_items.count() == 0:
                    return (Response(status=404, data="購物車未匹配任何資料"))
                # 计算订单总额
                total = 0
                for cart_item in cart_items:
                    total += int(cart_item.price) * cart_item.quantity
                if Member.objects.filter(uid=request.user.uid).count() != 1:
                    return (Response(status=400, data="人?"))
                oid = "OD{0:06d}".format(Order.objects.all().count()+14)
                # 创建订单
                order_data = {
                    'oid': oid,
                    'uid': request.user.uid,  # 假设购物车数据与订单关联的用户是相同的
                    'order_time': timezone.now(),  # 你需要提供订单时间
                    'complete_time': None,  # 订单完成时间初始化为None，你需要在订单完成时更新它
                    'total': str(total),  # 将总额设置为购物车商品价格的总和
                    'status': '未接單'  # 订单初始状态
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
                        product = Goods.objects.get(
                            gid=cart_item.gid_id)  # 假设产品有一个id字段
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

                    order_food_serializer = OrderFoodSerializer(
                        data=order_food_data)
                    if order_food_serializer.is_valid():
                        order_food_serializer.save()
                    else:
                        return Response(order_food_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                # 创建订单支付方式（示例中为信用卡）
                order_payment_data = {
                    'oid': order_serializer.data['oid'],
                    'method': request.data.get('payment_method', None),
                    'credit_number': request.data.get('credit_num', None),
                    'credit_private': request.data.get('credit_private', None),
                    'credit_date_year': request.data.get('credit_date_year', None),
                    'credit_date_month': request.data.get('credit_date_month', None)
                }

                order_payment_serializer = OrderPaymentSerializer(
                    data=order_payment_data)
                if order_payment_serializer.is_valid():
                    order_payment_serializer.save()
                else:
                    return Response(order_payment_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                # 删除购物车数据
                cart_items.delete()
                return Response("订单创建成功并购物车数据已删除", status=status.HTTP_201_CREATED)

        except Exception as e:
            # 处理错误，例如记录日志或发送通知
            return Response(f"發生錯誤：{e}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def __mail(self, target, oid):
        try:
            orders = Order.objects.filter(oid=oid).prefetch_related(
                'orderfoods', 'orderpayments')
            # 使用序列化器将订单数据序列化
            order_data = Order_output_Serializer(orders, many=True).data

            if mailto(action="send", data=ser.data):
                return (Response(status=200, data="OK"))
        except Order.DoesNotExist:
            return Response(data="訂單建立失敗_未新增成功", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            print(e)
            return Response(data="訂單通知出現錯誤！", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CartViewset(viewsets.ModelViewSet):
    """購物車"""
    serializer_class = Cart_serializer
    queryset = Cart.objects.all()

    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated])
    def add(self, request):
        # check member
        uid = request.user.uid
        member = MemberP.objects.filter(uid=uid)
        if member.count() != 1:
            return (Response(status=404, data="未知帳號"))
        # check  goods
        try:
            gid = request.data.get('gid', '')
            if Goods.objects.filter(gid=gid).count() != 1:
                return (Response(status=404, data="未知商品"))
        except Goods.DoesNotExist:
            return (Response(status=404, data="未知商品"))

        # check params
        quantity = request.data.get('quantity', '')
        # begin!
        import datetime
        current_time = datetime.datetime.now()
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        # 取得商品檢查數量
        Goods_ob = Goods.objects.filter(gid=gid)
        if int(Goods_ob[0].quantity)-int(quantity) < 0:
            return (Response(status=status.HTTP_400_BAD_REQUEST, data={'error': '商品數量不足！'}))
        try:
            if Cart.objects.get(gid_id=gid, uid_id=uid):
                Cart_data = Cart.objects.get(gid_id=gid, uid_id=uid)
                Cart_data.quantity = str(quantity)
                Cart_data.save()
                return Response(status=status.HTTP_202_ACCEPTED, data="已存在，購物車數量變動!")
        except Cart.DoesNotExist:
            try:
                cart_id = "CT{0:05d}".format(Cart.objects.all().count()+12)
                if Cart.objects.filter(cart_id=cart_id).count() == 1:
                    import random
                    cart_id = "CT{0:05d}".format(
                        Cart.objects.all().count()+random.randint(13, 30))
                new_ob = Cart.objects.create(
                    cart_id=cart_id,
                    quantity=quantity,
                    gid_id=gid,
                    price=Goods_ob[0].price,
                    uid_id=uid,
                    add_date=formatted_time
                )
                new_ob.save()
                return (Response(status=200, data="success"))
            except Exception as e:
                print(e)
                return ("請洽管理")

    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated])
    def change(self, request):
        uid = request.user.uid
        member = MemberP.objects.filter(uid=uid)
        if member.count() != 1:
            return (Response(status=404, data="未知帳號"))

        try:
            Cart_data = Cart.objects.get(
                cart_id=request.data.get('cart_id', ''))
            quantity = request.data.get('quantity', '')
            if quantity == '':
                return (Response(status=400, data="數量?"))
            else:
                Cart_data.quantity = str(quantity)
                Cart_data.save()
                return (Response(status=200, data="success"))
        except Cart.DoesNotExist:
            return (Response(status=404, data="未知購物車"))

    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated])
    def delete(self, request):
        uid = request.user.uid
        cart_id = request.data.get('cart_id', '')
        try:
            cart = Cart.objects.filter(uid_id=uid, cart_id=cart_id)
            if cart.exists():
                cart.delete()
                return (Response(status=200, data="success"))
            else:
                return (Response(status=404, data="購物車未知"))
        except Cart.DoesNotExist:
            return (Response(status=404, data="購物車未知"))

    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated])
    def get(self, request):
        uid = request.user.uid
        if MemberP.objects.filter(uid=uid).count() != 1:
            return (Response(status=404, data="未知帳號"))
        # begin!
        ob = Cart.objects.select_related('gid__sid').filter(uid_id=uid)
        serializer = Cart_serializer(ob, many=True)
        return (Response(status=200, data=serializer.data))

    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated])
    def getid(self, request):
        import json
        uid = request.user.uid
        if MemberP.objects.filter(uid=uid).count() != 1:
            return (Response(status=404, data="未知帳號"))
        # begin!
        data_list = request.data.get('cart_list', [])
        ob = Cart.objects.select_related('gid__sid').filter(cart_id=data_list)
        serializer = Cart_serializer(ob, many=True)
        return (Response(status=200, data=serializer.data))

    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated])
    def check(self, request):
        uid = request.user.uid
        if MemberP.objects.filter(uid=uid).count() != 1:
            return (Response(status=404, data="未知帳號"))
        # begin!
        ob = Cart.objects.select_related('gid__sid').filter(uid_id=uid)
        serializer = Cart_serializer(ob, many=True)
        return (Response(status=200, data=serializer.data))

    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated])
    def check_info(self, request):
        uid = request.user.uid
        from django.db import transaction
        with transaction.atomic():
            try:
                memob = Member.objects.get(uid=uid)
                if not request.GET.get('cart_id'):
                    ob = Cart.objects.filter(
                        uid=memob, cart_id=request.data.get('cart_id'))
                else:
                    return (Response(status=404, data="未給予購物車編號"))
                serializer = Cart_serializer(ob, many=True)
                # 計算總total
                total = 0
                for item in serializer.data:
                    total += (int(item['price'])*int(item['quantity']))
                result = {'total': total, 'data': serializer.data}
                return (Response(status=200, data=result))
            except Member.DoesNotExist:
                return (Response(status=404, data="會員?"))
            except Cart.DoesNotExist:
                return (Response(status=404, data="購物車未找到"))
            except Exception as e:
                print(e)
                return (Response(status=500, data="出現問題，請洽後端，問題：{}".format(e)))


def mailto(action, email, data):
    from notice.app import Email
    Email = Email()
    data = {}
    if action == 'complete':
        try:
            Email.order_complete(to_email=email, data=data)
            return (True)
        except Exception as e:
            print(e)
            return (False)
    elif action == 'cancel':
        try:
            Email.order_cancel(to_email=email, data=data)
            return (True)
        except Exception as e:
            print(e)
            return (False)
    elif action == 'send':
        try:
            Email.order_send(to_email=email, data=data)
            return (True)
        except Exception as e:
            print(e)
            return (False)
    else:
        raise KeyError('action is not found, action=complete,cancel,send')
