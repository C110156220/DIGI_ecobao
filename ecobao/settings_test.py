"""
測試專用設定 / Test-only settings.

以 SQLite in-memory 取代 MySQL，讓測試無須任何外部資料庫即可執行：

    python manage.py test --settings=ecobao.settings_test

Media 檔案寫入暫存目錄，避免測試污染 repo 內的 assets/。
"""

import tempfile

from .settings import *  # noqa: F401,F403

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# 測試期間不需要真實金鑰。
SECRET_KEY = 'test-only-secret-key-not-used-in-production'
DEBUG = False
ALLOWED_HOSTS = ['*']

# 避免測試把上傳圖片寫進 repo 的 assets/。
MEDIA_ROOT = tempfile.mkdtemp(prefix='ecobao-test-media-')

# 測試不應真的寄信。
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# 加速密碼雜湊。
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']
