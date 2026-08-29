"""
測試共用工具 / Shared test helpers.

集中建立測試資料（會員、店家、商品、活動）與取得 JWT 的邏輯，
避免每個 app 的 tests.py 重複拼裝 model 之間的關聯。
"""

import datetime

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from activity.models import Activity
from data_maintenance.models import Member, Store
from goods.models import Evaluate, Goods
from order.models import Cart


def create_member(uid='M00001', account='alice', password='pw-alice-123',
                  phone='0900000001', **extra):
    """建立一組 MemberP（登入帳號）+ Member（個資），回傳 (memberp, member)。"""
    user_model = get_user_model()
    memberp = user_model.objects.create_user(
        uid=uid,
        account=account,
        password=password,
        is_active=True,
        is_staff=False,
        is_superuser=False,
    )
    member = Member.objects.create(
        uid=memberp,
        name=extra.get('name', 'Alice'),
        phone=phone,
        gender=extra.get('gender', 'F'),
        email=extra.get('email', 'alice@example.com'),
        address=extra.get('address', '高雄市三民區建工路415號'),
        birth=extra.get('birth', datetime.date(1999, 1, 1)),
        allergen=extra.get('allergen', ''),
        prefer=extra.get('prefer'),
    )
    return memberp, member


def create_store(member, sid='S00001', name='好味小吃店', type='中式',
                 area='三民區', **extra):
    """以既有 Member 為店主建立 Store（Store 的 PK 就是 Member）。"""
    return Store.objects.create(
        sid=sid,
        upid=member,
        type=type,
        name=name,
        phone=extra.get('phone', '073814526'),
        email=extra.get('email', 'store@example.com'),
        intro=extra.get('intro', '示範店家'),
        city=extra.get('city', '高雄市'),
        area=area,
        address=extra.get('address', '高雄市三民區建工路415號'),
        lng=extra.get('lng', 120.4002),
        lat=extra.get('lat', 22.7725),
        on_business=extra.get('on_business', True),
    )


def create_goods(store, gid='G00001', name='招牌便當', price='60',
                 quantity='10', status=True, **extra):
    return Goods.objects.create(
        gid=gid,
        type=extra.get('type', '中式'),
        sid=store,
        name=name,
        intro=extra.get('intro', '今日剩餘餐點'),
        quantity=quantity,
        price=price,
        ingredient=extra.get('ingredient', '米飯,雞肉'),
        allergen=extra.get('allergen', "['蛋']"),
        status=status,
    )


def create_evaluate(store, member, evaid='EV00001', star=4, explain='好吃'):
    return Evaluate.objects.create(
        evaid=evaid, sid=store, uid=member, star=star, explain=explain,
    )


def create_cart(member, goods, cart_id='CT00001', quantity=2):
    return Cart.objects.create(
        cart_id=cart_id,
        uid=member,
        gid=goods,
        quantity=quantity,
        price=goods.price,
    )


def create_activity(actid='ACT00001', title='一起減少剩食', status=True, **extra):
    return Activity.objects.create(
        actid=actid,
        title=title,
        author=extra.get('author', '環飽小編'),
        upload_date=extra.get('upload_date', datetime.date(2023, 10, 1)),
        down_date=extra.get('down_date', datetime.date(2030, 10, 1)),
        content=extra.get('content', '活動內文'),
        status=status,
    )


def auth_client(memberp):
    """回傳一個已帶入該帳號 JWT 的 APIClient。"""
    from rest_framework_simplejwt.tokens import RefreshToken

    client = APIClient()
    token = RefreshToken.for_user(memberp)
    client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(token.access_token))
    return client
