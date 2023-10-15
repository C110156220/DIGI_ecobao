
from rest_framework import serializers
from .models import *
class Cart_serializer(serializers.ModelSerializer):
    class Meta:
        Model = Cart
        fields = "__all__"


class OrderPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderPayment
        fields = '__all__'

class OrderFoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderFood
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    payment = OrderPaymentSerializer()
    foods = OrderFoodSerializer(many=True)

    class Meta:
        model = Order
        fields = '__all__'

    def create(self, validated_data):
        payment_data = validated_data.pop('payment')
        foods_data = validated_data.pop('foods')

        # 创建订单支付
        payment = OrderPayment.objects.create(**payment_data)

        # 创建订单食品详情
        foods = [OrderFood.objects.create(**food_data) for food_data in foods_data]

        # 创建订单，并关联订单支付和订单食品详情
        order = Order.objects.create(payment=payment, **validated_data)
        order.foods.set(foods)

        return order
