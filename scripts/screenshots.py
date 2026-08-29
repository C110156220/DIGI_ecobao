"""
重新產生 README 用的截圖 / Regenerate the README screenshots.

需求：本機已安裝 Google Chrome，並已安裝 requirements-dev.txt。

    python manage.py migrate   --settings=ecobao.settings_demo
    python manage.py seed_demo --settings=ecobao.settings_demo
    DJANGO_SUPERUSER_PASSWORD=demo1234 python manage.py createsuperuser \
        --noinput --account admin --uid M00000 --settings=ecobao.settings_demo
    python manage.py runserver 8123 --settings=ecobao.settings_demo --noreload &
    python scripts/screenshots.py

輸出：docs/screenshots/*.png
"""

import os
import time

from PIL import Image, ImageChops
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

BASE = os.environ.get('DEMO_BASE_URL', 'http://127.0.0.1:8123')
ADMIN_ACCOUNT = os.environ.get('DEMO_ADMIN_ACCOUNT', 'admin')
ADMIN_PASSWORD = os.environ.get('DEMO_ADMIN_PASSWORD', 'demo1234')
OUT = os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), 'docs', 'screenshots')

WIDTH = 1440
MAX_HEIGHT = 2100

PAGES_AUTHENTICATED = [
    ('/default/admin/', '02-admin-dashboard'),
    ('/default/admin/data_maintenance/store/', '03-admin-stores'),
    ('/default/admin/goods/goods/', '04-admin-goods'),
    ('/default/admin/activity/activity/', '05-admin-activities'),
]

PAGES_ANONYMOUS = [
    ('/Goods/all/', '06-api-goods-all'),
    ('/store_sch/score/?sid=S00001', '07-api-store-score'),
]


def postprocess(path):
    """裁掉底部留白，並把 2x 圖縮成 1x 以控制 repo 體積。"""
    image = Image.open(path).convert('RGB')
    width, height = image.size
    background = Image.new('RGB', image.size, image.getpixel((width - 5, height - 5)))
    box = ImageChops.difference(image, background).getbbox()
    if box:
        image = image.crop((0, 0, width, min(height, box[3] + 60)))
    image = image.crop((0, 0, image.size[0], min(image.size[1], MAX_HEIGHT)))
    image = image.resize((image.size[0] // 2, image.size[1] // 2), Image.LANCZOS)
    image.save(path, optimize=True)


def main():
    os.makedirs(OUT, exist_ok=True)

    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--hide-scrollbars')
    options.add_argument('--force-device-scale-factor=2')
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(WIDTH, 1000)

    def shot(path, name, grow=True):
        driver.get(BASE + path)
        time.sleep(1.0)
        if grow:
            height = driver.execute_script(
                'return Math.max(document.body.scrollHeight,'
                ' document.documentElement.scrollHeight);')
            driver.set_window_size(WIDTH, min(max(height + 120, 700), MAX_HEIGHT))
            time.sleep(0.5)
        target = os.path.join(OUT, name + '.png')
        driver.save_screenshot(target)
        postprocess(target)
        driver.set_window_size(WIDTH, 1000)
        print('saved', target)

    try:
        shot('/default/admin/login/', '01-admin-login', grow=False)

        driver.get(BASE + '/default/admin/login/')
        time.sleep(0.6)
        driver.find_element(By.NAME, 'username').send_keys(ADMIN_ACCOUNT)
        driver.find_element(By.NAME, 'password').send_keys(ADMIN_PASSWORD)
        driver.find_element(By.CSS_SELECTOR, 'input[type=submit]').click()
        time.sleep(1.2)

        for path, name in PAGES_AUTHENTICATED:
            shot(path, name)

        driver.delete_all_cookies()
        for path, name in PAGES_ANONYMOUS:
            shot(path, name)
    finally:
        driver.quit()


if __name__ == '__main__':
    main()
