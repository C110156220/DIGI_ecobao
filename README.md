# 環飽 EcoBǎo — 剩食訂購平台 Backend

> A food-surplus (剩食) ordering platform that connects stores with surplus food to
> customers looking for affordable meals — reducing food waste while lowering the cost
> of eating. This repository is the **Django REST backend** powering both the customer
> app and the store portal.

環飽 EcoBǎo 是一個「剩食」訂購平台。餐飲店家可將當日未售完、即將報廢的餐點以優惠價上架，
消費者則能即時搜尋、下單並取餐，達成 **減少食物浪費** 與 **降低用餐成本** 的雙贏。
本專案為平台的 **後端 REST API**，同時服務「消費者端」與「店家端」。

---

## 功能總覽 Features

- **會員系統**：以自訂 `MemberP` 使用者模型搭配 JWT (SimpleJWT) 進行註冊、登入與權限控管。
- **店家入口 Store Portal**：店家資料維護、營業時間、商品（剩食）上架與管理。
- **商品與搜尋**：商品瀏覽、店家搜尋、圖片上傳（Pillow 壓縮處理）。
- **訂單流程**：購物車、下單、訂單查詢、接單／完成／取消狀態流轉。
- **Email 通知**：訂單狀態變更時，以 Jinja2 HTML 模板寄送 Gmail SMTP 通知信。
- **活動／新聞**：平台活動與最新消息發布。
- **地理編碼**：透過 Google Maps Geocoding API 將店家地址轉為經緯度。

---

## 技術棧 Tech Stack

| 類別 | 技術 |
| --- | --- |
| Language | Python 3.11 |
| Framework | Django 4.1 |
| API | Django REST Framework |
| Auth | djangorestframework-simplejwt (JWT) |
| Database | MySQL |
| CORS | django-cors-headers |
| Rate limiting | django-ratelimit |
| Images | Pillow |
| Email templating | Jinja2 + Gmail SMTP |
| Geocoding | Google Maps Geocoding API |
| Config | python-dotenv (`.env`) |

---

## 系統架構 Architecture

專案採 Django 多 app 架構，各司其職：

| App | 職責 Responsibility |
| --- | --- |
| `ecobao` | 專案設定（`settings.py`）、根路由（`urls.py`）、WSGI/ASGI 進入點。 |
| `data_maintenance` | 核心資料網域：自訂使用者 `MemberP`、會員 `Member`、員工 `Employee`、店家 `Store` 與營業時間 `Store_open`；登入 / 註冊 / 個資 / 店家資料 API 與 JWT serializer。 |
| `goods` | 商品（剩食）`Goods` 與店家評論 `Evaluate`；商品瀏覽、店家上傳商品、評論 API。 |
| `order` | 購物車 `Cart`、訂單 `Order`、訂單品項 `OrderFood`、付款 `OrderPayment`、接單 / 取消 `Ordercheck` / `OrderCancel`；下單與訂單查詢 API。 |
| `activity` | 平台活動 / 新聞 `Activity`（含首圖等多張圖片）。 |
| `notice` | Email 通知模組（`Email` 類別 + `order.html` Jinja2 模板），供 `order` app 呼叫寄送訂單通知信。 |

> 註：`INSTALLED_APPS` 目前註冊 `activity`、`goods`、`order`、`data_maintenance`；`notice`
> 以一般 Python 模組方式被 `order.views` 匯入使用。

### 權限預設 Permissions

DRF 全域預設為 `IsAuthenticated`（見 `settings.py` 的 `REST_FRAMEWORK`）。
公開 endpoint 於各 view/action 以 `@permission_classes([AllowAny])`（必要時搭配
`authentication_classes=[]`）明確覆寫，例如商品瀏覽、店家查詢、註冊等。

### 開發用腳本 Dev scripts

`scripts/seed/` 提供本機開發用的資料填充腳本（`random_account.py`、`random_add.py`），
詳見 `scripts/seed/README.md`。僅供本機開發，非正式環境使用。

---

## API 總覽 API Overview

Base URL 例：`http://localhost:8000/`

### 認證 Authentication

| Method | Endpoint | 說明 |
| --- | --- | --- |
| POST | `/api/token/obtain/` | 取得 JWT access / refresh token |
| POST | `/api/token/refresh/` | 以 refresh token 換發新的 access token |
| POST | `/api/token/verify/` | 驗證 token 有效性 |
| POST | `/Member/login/` | 會員登入（回傳 JWT） |
| POST | `/Store/check/` | 店家登入驗證 |

### 資源 Resources（DRF Router）

| Endpoint | ViewSet | 說明 |
| --- | --- | --- |
| `/member/` | `MemberAPIViews` | 會員基本資料 |
| `/memberP/` | `MemberP_Viewset` | 會員隱私 / 帳號資料 |
| `/register/` | `Member_register_APIViews` | 會員註冊 |
| `/store_data/` | `Store_data_Viewset` | 店家資料維護 |
| `/store_sch/` | `Store_search_Viewset` | 店家搜尋 |
| `/store_data/goods/` | `Goods_Upload_Viewsets` | 店家上架 / 管理商品 |
| `/Goods/` | `Goods_Viewset` | 商品瀏覽 |
| `/Evaluate/` | `Evaluate_store_Viewset` | 店家評論 |
| `/cart/` | `CartViewset` | 購物車 |
| `/order/` | `OrderViewset` | 訂單（下單、狀態流轉、通知） |
| `/orderv/` | `Order_read_Viewset` | 訂單查詢 |
| `/news/` | `Activity_Get_APIViews` | 活動 / 新聞 |
| `/default/admin` | Django Admin | 後台管理 |

> 各 ViewSet 標準支援 REST 動詞（`GET` / `POST` / `PUT` / `PATCH` / `DELETE`），
> 部分附有自訂 action（如訂單通知）。詳見各 app 的 `views.py`。

---

## 開發環境設定 Getting Started

### 前置需求 Prerequisites
- Python 3.11+
- MySQL 8.x（建立一個名為 `ecobao` 的資料庫）

### 步驟 Steps

```bash
# 1. 建立並啟用虛擬環境
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 2. 安裝相依套件
pip install -r requirements.txt

# 3. 設定環境變數
cp .env.example .env
#   接著編輯 .env，填入 SECRET_KEY、資料庫連線、Email、Google Maps API key 等。
#   產生 SECRET_KEY：
#   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# 4. 建立資料表
python manage.py migrate

# 5. （選用）建立管理者帳號
python manage.py createsuperuser

# 6. 啟動開發伺服器
python manage.py runserver
```

伺服器預設運行於 `http://127.0.0.1:8000/`。

---

## 環境變數 Environment Variables

所有敏感設定皆已抽離至環境變數，請參考 [`.env.example`](./.env.example)：

| 變數 | 說明 |
| --- | --- |
| `SECRET_KEY` | Django 密鑰（正式環境務必更換） |
| `DEBUG` | 除錯模式（正式環境設為 `False`） |
| `ALLOWED_HOSTS` | 允許的主機（逗號分隔） |
| `DB_ENGINE` / `DB_NAME` / `DB_USER` / `DB_PASSWORD` / `DB_HOST` / `DB_PORT` | 資料庫連線 |
| `CORS_ALLOWED_ORIGINS` | 允許跨域來源（逗號分隔） |
| `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` | Gmail SMTP 帳號與應用程式密碼 |
| `GOOGLE_MAPS_API_KEY` | Google Maps Geocoding API 金鑰 |

> **安全提醒**：`.env` 已列入 `.gitignore`，請勿提交任何真實金鑰至版本控制。

---

## 授權 License

本專案作為個人作品集（portfolio）用途展示。
