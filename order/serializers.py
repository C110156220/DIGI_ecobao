
from rest_framework import serializers
from .models import *
class Cart_serializer(serializers.ModelSerializer):
    goods_name = serializers.SerializerMethodField()
    store_name = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = "__all__"

    def get_goods_name(self, cart_item):
        return cart_item.gid.name

    def get_store_name(self, cart_item):
        return cart_item.gid.sid.name

class OrderSerializer(serializers.Serializer):
    # 將 uid 和 oid 定義為 CharField
    oid = serializers.CharField(max_length=50)
    uid = serializers.CharField(max_length=50)  # 請根據你的需求設置適當的最大長度
    order_time = serializers.DateTimeField()
    complete_time = serializers.DateTimeField(allow_null=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2)
    status = serializers.CharField(max_length=20)
    def create(self, validated_data):
        # 解析字串 uid 並查找相應的 Member 實例
        uid_str = validated_data['uid']
        member = Member.objects.get(uid=uid_str)

        # 創建 Order 實例，將 uid 設置為相應的 Member 實例
        order = Order(
            oid = validated_data['oid'],
            uid=member,
            order_time=validated_data['order_time'],
            complete_time=validated_data['complete_time'],
            total=validated_data['total'],
            status=validated_data['status']
        )
        order.save()
        return order

class OrderFoodSerializer(serializers.Serializer):
    # 將 oid 定義為 CharField
    oid = serializers.CharField(max_length=50)  # 請根據你的需求設置適當的最大長度
    gid = serializers.CharField(max_length=50)
    quantity = serializers.IntegerField()
    discount = serializers.DecimalField(max_digits=5, decimal_places=2,allow_null=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2)
    def create(self, validated_data):
        oid = validated_data.get('oid') ; gid = validated_data.get('gid')
        oid = Order.objects.get(oid=oid) ; gid=Goods.objects.get(gid=gid)
        order = OrderFood(
            oid = oid,
            gid = gid,
            quantity = validated_data['quantity'],
            discount = validated_data['discount'],
            subtotal = validated_data['subtotal']
        )
        order.save()
        return order

class OrderPaymentSerializer(serializers.Serializer):
    # 將 oid 定義為 CharField
    oid = serializers.CharField(max_length=50)  # 請根據你的需求設置適當的最大長度
    method = serializers.CharField(max_length=20)
    credit_number = serializers.CharField(max_length=16,allow_null=True)
    credit_private = serializers.CharField(max_length=4,allow_null=True)
    credit_date_year = serializers.IntegerField(allow_null=True)
    credit_date_month = serializers.IntegerField(allow_null=True)
    def create(self, validated_data):
        oid = validated_data.get('oid');oid = Order.objects.get(oid=oid)
        order = OrderPayment(
            oid = oid,
            method = validated_data['method'],
            credit_number = validated_data['credit_number'],
            credit_private = validated_data['credit_private'],
            credit_date_year = validated_data['credit_date_year'],
            credit_date_month = validated_data['credit_date_month']
        )
        order.save()
        return order
