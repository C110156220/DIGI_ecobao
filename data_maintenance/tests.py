"""會員註冊 / JWT 登入 / 店家查詢 API 測試。"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from data_maintenance.models import Member, MemberP, Store
from data_maintenance.serializers import get_id
from ecobao.testutils import (
    auth_client, create_evaluate, create_member, create_store,
)


VALID_REGISTRATION = {
    'name': 'Carol',
    'phone': '0912345678',
    'gender': 'F',
    'email': 'carol@example.com',
    'address': '高雄市三民區建工路415號',
    'birth': '2000-05-20',
    'allergen': '',
    'account': 'carol',
    'password': 'carol-pw-123',
}


class MemberRegistrationTests(TestCase):
    """/register/new/ — 註冊同時建立 MemberP（帳密）與 Member（個資）。"""

    def setUp(self):
        self.client = APIClient()

    def test_registration_creates_memberp_and_member(self):
        response = self.client.post(
            '/register/new/', VALID_REGISTRATION, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(MemberP.objects.count(), 1)
        self.assertEqual(Member.objects.count(), 1)

        memberp = MemberP.objects.get(account='carol')
        member = Member.objects.get(uid=memberp)
        self.assertEqual(member.name, 'Carol')
        self.assertEqual(memberp.uid, member.uid_id)

    def test_registration_hashes_the_password(self):
        """密碼必須雜湊儲存，絕不可明文落地。"""
        self.client.post('/register/new/', VALID_REGISTRATION, format='json')

        memberp = MemberP.objects.get(account='carol')
        self.assertNotEqual(memberp.password, 'carol-pw-123')
        self.assertTrue(memberp.check_password('carol-pw-123'))

    def test_registration_is_public(self):
        """註冊必須允許未登入者呼叫。"""
        response = self.client.post(
            '/register/new/', VALID_REGISTRATION, format='json')

        self.assertNotIn(response.status_code, (401, 403))

    def test_duplicate_account_is_rejected(self):
        self.client.post('/register/new/', VALID_REGISTRATION, format='json')

        duplicate = dict(VALID_REGISTRATION, phone='0999999999')
        response = self.client.post('/register/new/', duplicate, format='json')

        self.assertEqual(response.status_code, 404)
        self.assertEqual(MemberP.objects.filter(account='carol').count(), 1)

    def test_missing_required_field_is_rejected(self):
        """缺必填欄位須擋下，且不得建立任何資料。

        迴歸測試：舊版以 `'' in data` 檢查 dict 的 key，此驗證形同虛設。
        """
        for field in ('name', 'phone', 'gender', 'email', 'address',
                      'birth', 'account', 'password'):
            with self.subTest(field=field):
                payload = dict(VALID_REGISTRATION, **{field: ''})
                response = self.client.post(
                    '/register/new/', payload, format='json')

                self.assertEqual(response.status_code, 404)
                self.assertEqual(MemberP.objects.count(), 0)
                self.assertEqual(Member.objects.count(), 0)

    def test_blank_allergen_is_allowed(self):
        """過敏原為選填，留空仍應註冊成功。"""
        response = self.client.post(
            '/register/new/', dict(VALID_REGISTRATION, allergen=''),
            format='json')

        self.assertEqual(response.status_code, 200)


class JWTLoginTests(TestCase):
    """JWT 取得 / 驗證，以及自訂 token claims。"""

    def setUp(self):
        self.client = APIClient()
        self.memberp, self.member = create_member(
            uid='M00001', account='alice', password='pw-alice-123')

    def test_obtain_token_with_valid_credentials(self):
        response = self.client.post(
            '/api/token/obtain/',
            {'account': 'alice', 'password': 'pw-alice-123'}, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.json())
        self.assertIn('refresh', response.json())

    def test_obtain_token_with_wrong_password_is_rejected(self):
        response = self.client.post(
            '/api/token/obtain/',
            {'account': 'alice', 'password': 'wrong-password'}, format='json')

        self.assertEqual(response.status_code, 401)

    def test_token_carries_uid_and_account_claims(self):
        """Member_TokenObtainPairSerializer 應將 uid / account 寫入 token。"""
        from rest_framework_simplejwt.tokens import AccessToken

        response = self.client.post(
            '/api/token/obtain/',
            {'account': 'alice', 'password': 'pw-alice-123'}, format='json')
        token = AccessToken(response.json()['access'])

        self.assertEqual(token['uid'], 'M00001')
        self.assertEqual(token['account'], 'alice')

    def test_refresh_token_yields_new_access_token(self):
        refresh = self.client.post(
            '/api/token/obtain/',
            {'account': 'alice', 'password': 'pw-alice-123'},
            format='json').json()['refresh']

        response = self.client.post(
            '/api/token/refresh/', {'refresh': refresh}, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.json())

    def test_get_id_helper_resolves_account_to_uid(self):
        self.assertEqual(get_id('alice'), 'M00001')

    def test_get_id_helper_returns_empty_for_unknown_account(self):
        self.assertEqual(get_id('does-not-exist'), '')


class ProtectedEndpointTests(TestCase):
    """全域預設為 IsAuthenticated，受保護端點須擋下匿名請求。"""

    def test_member_account_requires_authentication(self):
        response = APIClient().get('/member/account/')

        self.assertEqual(response.status_code, 401)

    def test_member_account_returns_own_profile_when_authenticated(self):
        memberp, member = create_member()

        response = auth_client(memberp).get('/member/account/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Alice')


class StoreSearchTests(TestCase):
    """/store_sch/ — 店家搜尋與評分彙總。"""

    def setUp(self):
        self.client = APIClient()
        _, self.member_a = create_member(
            uid='M00001', account='alice', phone='0900000001')
        _, self.member_b = create_member(
            uid='M00002', account='bob', phone='0900000002')
        self.store_a = create_store(
            self.member_a, sid='S00001', name='好味小吃店',
            type='中式', area='三民區')
        self.store_b = create_store(
            self.member_b, sid='S00002', name='美味日式屋',
            type='日式', area='左營區')

    def test_all_returns_every_store(self):
        response = self.client.get('/store_sch/all/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)

    def test_type_filters_by_food_type(self):
        response = self.client.get('/store_sch/type/', {'type': '日式'})

        self.assertEqual(response.status_code, 200)
        names = [item['name'] for item in response.json()]
        self.assertEqual(names, ['美味日式屋'])

    def test_type_all_keyword_returns_every_store(self):
        response = self.client.get('/store_sch/type/', {'type': 'all'})

        self.assertEqual(len(response.json()), 2)

    def test_type_without_param_returns_404(self):
        self.assertEqual(self.client.get('/store_sch/type/').status_code, 404)

    def test_search_matches_partial_name(self):
        response = self.client.get('/store_sch/search/', {'name': '味'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)

        response = self.client.get('/store_sch/search/', {'name': '日式'})
        self.assertEqual(len(response.json()), 1)

    def test_search_without_param_returns_404(self):
        self.assertEqual(self.client.get('/store_sch/search/').status_code, 404)

    def test_id_returns_matching_store(self):
        response = self.client.get('/store_sch/id/', {'sid': 'S00002'})

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(len(body), 1)
        self.assertEqual(body[0]['name'], '美味日式屋')

    def test_score_averages_and_floors_ratings(self):
        """評分為所有評論星等平均後無條件捨去。"""
        create_evaluate(self.store_a, self.member_a, evaid='EV00001', star=5)
        create_evaluate(self.store_a, self.member_b, evaid='EV00002', star=4)

        response = self.client.get('/store_sch/score/', {'sid': 'S00001'})

        self.assertEqual(response.status_code, 200)
        # (5 + 4) / 2 = 4.5 -> floor -> 4
        self.assertEqual(response.json(), {'rating': 4})

    def test_score_is_zero_when_store_has_no_reviews(self):
        response = self.client.get('/store_sch/score/', {'sid': 'S00002'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'rating': 0})

    def test_score_for_unknown_store_returns_404(self):
        response = self.client.get('/store_sch/score/', {'sid': 'S99999'})

        self.assertEqual(response.status_code, 404)


class StoreLoginCheckTests(TestCase):
    """/Store/check/ — 驗證登入者是否具店家身分。"""

    def test_member_with_store_is_greeted(self):
        memberp, member = create_member()
        create_store(member, name='好味小吃店')

        response = auth_client(memberp).get('/Store/check/')

        self.assertEqual(response.status_code, 200)
        self.assertIn('好味小吃店', response.json())

    def test_anonymous_is_rejected(self):
        self.assertEqual(APIClient().get('/Store/check/').status_code, 401)


class CustomUserManagerTests(TestCase):
    """自訂 MemberP 使用者模型。"""

    def test_create_user_sets_usable_hashed_password(self):
        user = get_user_model().objects.create_user(
            uid='M09999', account='dave', password='dave-pw-123',
            is_active=True, is_staff=False, is_superuser=False)

        self.assertNotEqual(user.password, 'dave-pw-123')
        self.assertTrue(user.check_password('dave-pw-123'))

    def test_create_superuser_sets_staff_and_superuser_flags(self):
        user = get_user_model().objects.create_superuser(
            account='root', password='root-pw-123', uid='M09998')

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_active)

    def test_account_is_the_username_field(self):
        self.assertEqual(MemberP.USERNAME_FIELD, 'account')


class StoreProximityTests(TestCase):
    """/store_sch/device_around/ — 依裝置座標找 5 公里內的店家。

    迴歸測試：此端點依賴 geopy，該套件原本漏列於 requirements.txt，
    在乾淨環境會直接 ImportError。
    """

    def setUp(self):
        self.client = APIClient()
        # 高雄三民區
        _, member_near = create_member(
            uid='M00001', account='near', phone='0900000001')
        self.near = create_store(
            member_near, sid='S00001', name='附近小吃店',
            lng=120.4002, lat=22.7725)
        # 臺北大安區（距離高雄約 300 公里）
        _, member_far = create_member(
            uid='M00002', account='far', phone='0900000002')
        self.far = create_store(
            member_far, sid='S00002', name='遙遠日食',
            lng=121.5436, lat=25.0263)

    def test_only_stores_within_radius_are_returned(self):
        response = self.client.post(
            '/store_sch/device_around/',
            {'lat': '22.7725', 'lng': '120.4002'}, format='json')

        self.assertEqual(response.status_code, 200)
        names = [item['name'] for item in response.json()]
        self.assertEqual(names, ['附近小吃店'])

    def test_returns_empty_list_when_nothing_is_nearby(self):
        """座標落在海上時應回傳空清單而非錯誤。"""
        response = self.client.post(
            '/store_sch/device_around/',
            {'lat': '0.0', 'lng': '0.0'}, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])
