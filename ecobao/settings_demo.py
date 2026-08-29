"""
Demo 模式設定 / Demo-mode settings.

讓任何人「不需要 MySQL、不需要任何金鑰」就能把後台跑起來看實際畫面：

    python manage.py migrate   --settings=ecobao.settings_demo
    python manage.py seed_demo --settings=ecobao.settings_demo
    python manage.py runserver --settings=ecobao.settings_demo

資料庫為專案根目錄下的 demo.sqlite3（已列入 .gitignore）。
僅供本機展示，切勿用於正式環境。
"""

from .settings import *  # noqa: F401,F403

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'demo.sqlite3',  # noqa: F405
    }
}

# Demo 用的固定金鑰，公開無妨——正式環境請改用 .env 的 SECRET_KEY。
SECRET_KEY = 'demo-only-secret-key-do-not-use-in-production'
DEBUG = True
ALLOWED_HOSTS = ['*']

# Demo 不寄真實信件，改印到 console。
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Demo 的媒體檔放在 demo_media/（已列入 .gitignore）。
MEDIA_ROOT = BASE_DIR / 'demo_media'  # noqa: F405
