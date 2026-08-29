"""商品（剩食）瀏覽 API 測試。"""

from django.test import TestCase
from rest_framework.test import APIClient

from ecobao.testutils import (
    auth_client, create_goods, create_member, create_store,
)
from goods.models import Goods
from goods.serializers import Goods_serializers


class GoodsBrowseAPITests(TestCase):
    """/Goods/ 之公開瀏覽端點。"""

    def setUp(self):
        self.client = APIClient()
        self.memberp, self.member = create_member()
        self.store = create_store(self.member)
        self.on_sale = create_goods(
            self.store, gid='G00001', name='招牌便當', price='60', status=True)
        self.off_sale = create_goods(
            self.store, gid='G00002', name='已下架湯品', price='30', status=False)

    def test_all_returns_only_available_goods(self):
        """/Goods/all/ 只回傳 status=True 的商品，下架商品不得外洩。"""
        response = self.client.get('/Goods/all/')

        self.assertEqual(response.status_code, 200)
        gids = [item['gid'] for item in response.json()]
        self.assertEqual(gids, ['G00001'])
        self.assertNotIn('G00002', gids)

    def test_all_is_public(self):
        """未登入即可瀏覽商品（AllowAny 覆寫全域 IsAuthenticated）。"""
        self.assertEqual(self.client.get('/Goods/all/').status_code, 200)

    def test_id_returns_single_goods(self):
        response = self.client.get('/Goods/id/', {'gid': 'G00001'})

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(len(body), 1)
        self.assertEqual(body[0]['name'], '招牌便當')
        self.assertEqual(body[0]['price'], '60')

    def test_id_without_param_returns_404(self):
        response = self.client.get('/Goods/id/')

        self.assertEqual(response.status_code, 404)

    def test_id_with_unknown_gid_returns_404(self):
        response = self.client.get('/Goods/id/', {'gid': 'G99999'})

        self.assertEqual(response.status_code, 404)

    def test_store_lists_goods_of_that_store(self):
        """/Goods/store/ 依 sid 取得該店家商品。"""
        response = self.client.get('/Goods/store/', {'sid': 'S00001'})

        self.assertEqual(response.status_code, 200)
        gids = sorted(item['gid'] for item in response.json())
        self.assertEqual(gids, ['G00001', 'G00002'])

    def test_store_without_param_returns_404(self):
        self.assertEqual(self.client.get('/Goods/store/').status_code, 404)


class GoodsSerializerTests(TestCase):
    """序列化器不得洩漏 sid 等內部欄位。"""

    def test_serializer_exposes_expected_fields_only(self):
        _, member = create_member()
        store = create_store(member)
        goods = create_goods(store)

        data = Goods_serializers(goods).data

        self.assertEqual(
            set(data.keys()),
            {'gid', 'type', 'name', 'intro', 'quantity', 'food_pic',
             'price', 'ingredient', 'allergen', 'status'},
        )


class GoodsStoreManagementTests(TestCase):
    """店家端商品上下架（/store_data/goods/）。"""

    def setUp(self):
        self.memberp, self.member = create_member()
        self.store = create_store(self.member)
        self.goods = create_goods(self.store, status=True)
        self.client = auth_client(self.memberp)

    def test_unavailable_marks_goods_off_sale(self):
        response = self.client.post(
            '/store_data/goods/unavailable/', {'gid': 'G00001'}, format='json')

        self.assertEqual(response.status_code, 200)
        self.goods.refresh_from_db()
        self.assertFalse(self.goods.status)

    def test_available_marks_goods_back_on_sale(self):
        self.goods.status = False
        self.goods.save()

        response = self.client.post(
            '/store_data/goods/available/', {'gid': 'G00001'}, format='json')

        self.assertEqual(response.status_code, 200)
        self.goods.refresh_from_db()
        self.assertTrue(self.goods.status)

    def test_unavailable_with_unknown_gid_returns_404(self):
        response = self.client.post(
            '/store_data/goods/unavailable/', {'gid': 'G99999'}, format='json')

        self.assertEqual(response.status_code, 404)

    def test_non_store_member_cannot_manage_goods(self):
        """非店家身分的會員不得上下架商品。"""
        plain_memberp, _ = create_member(
            uid='M00002', account='bob', phone='0900000002')

        response = auth_client(plain_memberp).post(
            '/store_data/goods/unavailable/', {'gid': 'G00001'}, format='json')

        self.assertEqual(response.status_code, 404)
        self.goods.refresh_from_db()
        self.assertTrue(self.goods.status)

    def test_anonymous_cannot_manage_goods(self):
        response = APIClient().post(
            '/store_data/goods/unavailable/', {'gid': 'G00001'}, format='json')

        self.assertEqual(response.status_code, 401)
        self.assertTrue(Goods.objects.get(gid='G00001').status)
