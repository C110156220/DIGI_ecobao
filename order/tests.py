"""購物車與訂單 API 測試。"""

from django.test import TestCase
from rest_framework.test import APIClient

from ecobao.testutils import (
    auth_client, create_cart, create_goods, create_member, create_store,
)
from order.models import Cart, Order, OrderFood
from order.serializers import Cart_serializer, Order_output_Serializer


class CartAPITests(TestCase):
    """/cart/ — 加入、修改、刪除、讀取購物車。"""

    def setUp(self):
        self.memberp, self.member = create_member()
        self.store = create_store(self.member, name='好味小吃店')
        self.goods = create_goods(
            self.store, gid='G00001', name='招牌便當', price='60', quantity='10')
        self.client = auth_client(self.memberp)

    def test_add_creates_cart_item(self):
        response = self.client.post(
            '/cart/add/', {'gid': 'G00001', 'quantity': 2}, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Cart.objects.count(), 1)

        item = Cart.objects.get()
        self.assertEqual(item.gid_id, 'G00001')
        self.assertEqual(item.uid_id, 'M00001')
        self.assertEqual(item.quantity, 2)
        # 價格於加入時自商品快照，避免日後改價影響既有購物車。
        self.assertEqual(item.price, '60')

    def test_adding_same_goods_twice_updates_quantity_instead_of_duplicating(self):
        self.client.post(
            '/cart/add/', {'gid': 'G00001', 'quantity': 2}, format='json')
        response = self.client.post(
            '/cart/add/', {'gid': 'G00001', 'quantity': 5}, format='json')

        self.assertEqual(response.status_code, 202)
        self.assertEqual(Cart.objects.count(), 1)
        self.assertEqual(Cart.objects.get().quantity, 5)

    def test_add_rejects_quantity_above_stock(self):
        """庫存 10 份，要求 11 份應被擋下且不建立購物車。"""
        response = self.client.post(
            '/cart/add/', {'gid': 'G00001', 'quantity': 11}, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Cart.objects.count(), 0)

    def test_add_allows_quantity_equal_to_stock(self):
        response = self.client.post(
            '/cart/add/', {'gid': 'G00001', 'quantity': 10}, format='json')

        self.assertEqual(response.status_code, 200)

    def test_add_unknown_goods_returns_404(self):
        response = self.client.post(
            '/cart/add/', {'gid': 'G99999', 'quantity': 1}, format='json')

        self.assertEqual(response.status_code, 404)
        self.assertEqual(Cart.objects.count(), 0)

    def test_add_requires_authentication(self):
        response = APIClient().post(
            '/cart/add/', {'gid': 'G00001', 'quantity': 1}, format='json')

        self.assertEqual(response.status_code, 401)
        self.assertEqual(Cart.objects.count(), 0)

    def test_change_updates_quantity(self):
        cart = create_cart(self.member, self.goods, cart_id='CT00001')

        response = self.client.post(
            '/cart/change/', {'cart_id': 'CT00001', 'quantity': 7},
            format='json')

        self.assertEqual(response.status_code, 200)
        cart.refresh_from_db()
        self.assertEqual(cart.quantity, 7)

    def test_change_unknown_cart_returns_404(self):
        response = self.client.post(
            '/cart/change/', {'cart_id': 'CT99999', 'quantity': 7},
            format='json')

        self.assertEqual(response.status_code, 404)

    def test_delete_removes_own_cart_item(self):
        create_cart(self.member, self.goods, cart_id='CT00001')

        response = self.client.post(
            '/cart/delete/', {'cart_id': 'CT00001'}, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Cart.objects.count(), 0)

    def test_cannot_delete_another_members_cart_item(self):
        """購物車刪除必須綁定 uid，不可跨帳號刪除他人資料。"""
        create_cart(self.member, self.goods, cart_id='CT00001')
        other_memberp, _ = create_member(
            uid='M00002', account='bob', phone='0900000002')

        response = auth_client(other_memberp).post(
            '/cart/delete/', {'cart_id': 'CT00001'}, format='json')

        self.assertEqual(response.status_code, 404)
        self.assertEqual(Cart.objects.count(), 1)

    def test_get_returns_only_own_cart_items(self):
        create_cart(self.member, self.goods, cart_id='CT00001', quantity=3)
        other_memberp, other_member = create_member(
            uid='M00002', account='bob', phone='0900000002')
        create_cart(other_member, self.goods, cart_id='CT00002', quantity=1)

        response = self.client.get('/cart/get/')

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(len(body), 1)
        self.assertEqual(body[0]['cart_id'], 'CT00001')

    def test_get_requires_authentication(self):
        self.assertEqual(APIClient().get('/cart/get/').status_code, 401)


class CartSerializerTests(TestCase):
    """購物車序列化器的衍生欄位。"""

    def setUp(self):
        self.memberp, self.member = create_member()
        self.store = create_store(
            self.member, name='好味小吃店', phone='073814526')
        self.goods = create_goods(
            self.store, gid='G00001', name='招牌便當', price='60')

    def test_subtotal_is_price_times_quantity(self):
        cart = create_cart(self.member, self.goods, quantity=3)

        data = Cart_serializer(cart).data

        self.assertEqual(data['subtotal'], 180)

    def test_serializer_denormalises_goods_and_store_details(self):
        cart = create_cart(self.member, self.goods, quantity=1)

        data = Cart_serializer(cart).data

        self.assertEqual(data['goods_name'], '招牌便當')
        self.assertEqual(data['goods_price'], '60')
        self.assertEqual(data['store_name'], '好味小吃店')
        self.assertEqual(data['store_phone'], '073814526')
        self.assertEqual(data['store_address'], self.store.address)


class OrderReadTests(TestCase):
    """/orderv/ — 訂單查詢。"""

    def setUp(self):
        import datetime

        from django.utils import timezone

        self.memberp, self.member = create_member()
        self.store = create_store(self.member, sid='S00001', name='好味小吃店')
        self.goods = create_goods(
            self.store, gid='G00001', name='招牌便當', price='60')
        self.order = Order.objects.create(
            oid='O00001',
            uid=self.member,
            order_time=timezone.make_aware(datetime.datetime(2023, 10, 1, 12, 0)),
            total='120',
            status='未接單',
        )
        OrderFood.objects.create(
            oid=self.order, gid=self.goods, quantity=2, discount=0, subtotal=120)
        self.client = auth_client(self.memberp)

    def test_all_returns_own_orders(self):
        response = self.client.get('/orderv/all/')

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(len(body), 1)
        self.assertEqual(body[0]['oid'], 'O00001')

    def test_all_requires_authentication(self):
        self.assertEqual(APIClient().get('/orderv/all/').status_code, 401)

    def test_order_output_serializer_nests_order_foods(self):
        data = Order_output_Serializer(self.order).data

        self.assertEqual(data['oid'], 'O00001')
        self.assertEqual(len(data['orderfoods']), 1)

        line = data['orderfoods'][0]
        self.assertEqual(line['goods_name'], '招牌便當')
        self.assertEqual(line['store_name'], '好味小吃店')
        self.assertEqual(line['sid'], 'S00001')
        self.assertEqual(line['quantity'], 2)
        self.assertEqual(line['subtotal'], 120)
