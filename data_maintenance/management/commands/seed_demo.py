"""
建立 demo 展示資料 / Seed demo data.

    python manage.py seed_demo --settings=ecobao.settings_demo

會建立一批示範會員、店家、剩食商品、評論與活動公告，
讓 Django Admin 與 DRF 瀏覽介面「一打開就有東西可看」。
資料皆為虛構，可重複執行（idempotent）。
"""

import datetime
import random

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from activity.models import Activity
from data_maintenance.models import Member, Store
from goods.models import Evaluate, Goods

DEMO_PASSWORD = 'demo1234'

STORES = [
    ('S00001', '惜食便當坊', '中式', '高雄市', '三民區', 120.4002, 22.7725),
    ('S00002', '晨光麵包舖', '西式', '高雄市', '左營區', 120.2945, 22.6885),
    ('S00003', '一期一會日食', '日式', '臺北市', '大安區', 121.5436, 25.0263),
    ('S00004', '綠芽蔬食', '素食', '臺中市', '西屯區', 120.6478, 24.1810),
    ('S00005', '深夜滷味攤', '滷味', '臺南市', '東區', 120.2185, 22.9908),
]

GOODS = [
    ('S00001', '招牌雞腿便當', '中式', '65', '8', '米飯,雞腿,青菜', "['蛋']"),
    ('S00001', '滷排骨便當', '中式', '60', '5', '米飯,豬肉,滷蛋', "['蛋','大豆']"),
    ('S00002', '隔日鮮奶吐司', '西式', '35', '12', '麵粉,鮮奶,奶油', "['麩質','乳製品']"),
    ('S00002', '肉桂捲', '西式', '45', '4', '麵粉,肉桂,奶油', "['麩質','乳製品']"),
    ('S00003', '鮭魚親子丼', '日式', '90', '3', '米飯,鮭魚,鮭魚卵', "['魚類']"),
    ('S00004', '五穀蔬食餐盒', '素食', '70', '6', '糙米,豆腐,時蔬', "['大豆']"),
    ('S00005', '綜合滷味拼盤', '滷味', '80', '10', '豆干,海帶,米血', "['大豆']"),
]

ACTIVITIES = [
    ('ACT00001', '為什麼我們要一起搶救剩食？',
     '台灣每年浪費的食物超過 300 萬公噸。環飽讓店家把當日未售完的餐點以優惠價上架，'
     '消費者省錢、店家減損、地球少一份負擔。'),
    ('ACT00002', '新手指南：三步驟完成第一筆惜食訂單',
     '一、搜尋你附近的店家；二、把即期餐點加入購物車；三、線上下單後於指定時段前往取餐。'),
    ('ACT00003', '店家招募中：讓你的剩食成為別人的晚餐',
     '免上架費，只要在打烊前把剩餘餐點放上平台，就能替店裡多賺一份收入並減少廚餘處理成本。'),
]


class Command(BaseCommand):
    help = '建立 demo 展示資料（會員 / 店家 / 商品 / 評論 / 活動）。'

    def add_arguments(self, parser):
        parser.add_argument(
            '--flush', action='store_true',
            help='先清除既有 demo 資料再重建。',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        random.seed(20231001)
        user_model = get_user_model()

        if options['flush']:
            Evaluate.objects.all().delete()
            Goods.objects.all().delete()
            Store.objects.all().delete()
            Member.objects.all().delete()
            user_model.objects.filter(is_superuser=False).delete()
            Activity.objects.all().delete()
            self.stdout.write('已清除既有 demo 資料。')

        members = {}
        for index, (sid, name, type_, city, area, lng, lat) in enumerate(STORES, start=1):
            uid = 'M{0:05d}'.format(index)
            account = 'store{0:02d}'.format(index)

            memberp = user_model.objects.filter(uid=uid).first()
            if memberp is None:
                memberp = user_model.objects.create_user(
                    uid=uid, account=account, password=DEMO_PASSWORD,
                    is_active=True, is_staff=False, is_superuser=False)

            member, _ = Member.objects.get_or_create(
                uid=memberp,
                defaults={
                    'name': '{}店長'.format(name),
                    'phone': '09{0:08d}'.format(index),
                    'gender': random.choice(['M', 'F']),
                    'email': '{}@example.com'.format(account),
                    'address': '{}{}示範路{}號'.format(city, area, index),
                    'birth': datetime.date(1990, 1, 1),
                    'allergen': '',
                    'prefer': None,
                },
            )
            members[sid] = member

            Store.objects.get_or_create(
                upid=member,
                defaults={
                    'sid': sid, 'type': type_, 'name': name,
                    'phone': '07{0:07d}'.format(index),
                    'email': '{}@example.com'.format(account),
                    'intro': '{}的即期惜食專區'.format(name),
                    'city': city, 'area': area,
                    'address': '{}{}示範路{}號'.format(city, area, index),
                    'lng': lng, 'lat': lat, 'on_business': True,
                },
            )

        # 另建一位純消費者，用來示範顧客端 API。
        customer_p = user_model.objects.filter(uid='M09001').first()
        if customer_p is None:
            customer_p = user_model.objects.create_user(
                uid='M09001', account='customer', password=DEMO_PASSWORD,
                is_active=True, is_staff=False, is_superuser=False)
        customer, _ = Member.objects.get_or_create(
            uid=customer_p,
            defaults={
                'name': '示範消費者', 'phone': '0988000001', 'gender': 'F',
                'email': 'customer@example.com', 'address': '高雄市三民區建工路415號',
                'birth': datetime.date(2000, 6, 15), 'allergen': "['花生']",
                'prefer': "['中式','日式']",
            },
        )

        for index, (sid, name, type_, price, qty, ingredient, allergen) in enumerate(GOODS, start=1):
            store = Store.objects.get(sid=sid)
            Goods.objects.get_or_create(
                gid='G{0:05d}'.format(index),
                defaults={
                    'type': type_, 'sid': store, 'name': name,
                    'intro': '今日未售完，特價回饋', 'quantity': qty,
                    'price': price, 'ingredient': ingredient,
                    'allergen': allergen, 'status': True,
                },
            )

        reviews = [
            ('S00001', 5, '便當份量很足，價格又便宜，會再回購！'),
            ('S00001', 4, '雞腿好吃，只是取餐時間有點趕。'),
            ('S00002', 5, '吐司隔日一樣鬆軟，烤過更香。'),
            ('S00003', 4, '親子丼新鮮，沒想到剩食也能這麼好。'),
            ('S00005', 3, '滷味還不錯，希望品項再多一點。'),
        ]
        for index, (sid, star, explain) in enumerate(reviews, start=1):
            Evaluate.objects.get_or_create(
                evaid='EV{0:05d}'.format(index),
                defaults={
                    'sid': Store.objects.get(sid=sid),
                    'uid': customer, 'star': star, 'explain': explain,
                },
            )

        for actid, title, content in ACTIVITIES:
            Activity.objects.get_or_create(
                actid=actid,
                defaults={
                    'title': title, 'author': '環飽小編',
                    'upload_date': datetime.date(2023, 10, 1),
                    'down_date': datetime.date(2030, 12, 31),
                    'content': content, 'status': True,
                },
            )

        self.stdout.write(self.style.SUCCESS(
            'Demo 資料完成：店家 {} 家、商品 {} 項、評論 {} 則、活動 {} 篇。'.format(
                Store.objects.count(), Goods.objects.count(),
                Evaluate.objects.count(), Activity.objects.count())))
        self.stdout.write(
            '示範帳號：store01 / customer，密碼皆為 {}'.format(DEMO_PASSWORD))
