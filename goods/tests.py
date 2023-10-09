from django.test import TestCase, Client
from django.urls import reverse

class APITestCase(TestCase):
    def setUp(self):
        # 在測試開始前設定
        self.client = Client()

    def test_api_endpoint_with_parameter(self):
        # 定義API端點的URL
        api_url = reverse('Goods/all')  # 替換為你的實際API端點名稱

        # 定義GET參數
        params = {'param': 'some_value'}

        # 發送帶有參數的GET請求
        response = self.client.get(api_url, params)

        # 斷言響應狀態碼是否為200
        self.assertEqual(response.status_code, 200)
