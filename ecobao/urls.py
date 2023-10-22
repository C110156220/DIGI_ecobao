from django.contrib import admin
from django.urls import path

# app.Views
import data_maintenance.views as dv
import goods.views as goodv
import activity.views as actv
import order.views as orv
# router settings
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

router = routers.SimpleRouter()
router.register(r'member', dv.MemberAPIViews,basename='會員')
router.register(r'memberP',dv.MemberP_Viewset,basename='會員(隱私)')
router.register(r'store_data', dv.Store_data_Viewset,basename='店家資料')
router.register(r'store_sch',dv.Store_search_Viewset,basename='查詢店家')
router.register(r'register',dv.Member_register_APIViews,basename='註冊')
router.register(r'Goods',goodv.Goods_Viewset,basename='商品')
router.register(r'store_data/goods',goodv.Goods_Upload_Viewsets,basename='店家上傳商品')
router.register(r'news',actv.Activity_Get_APIViews,basename='新聞')
router.register(r'Evaluate',goodv.Evaluate_store_Viewset,basename='評論')
router.register(r'order',orv.OrderViewset,basename='訂單')
router.register(r'cart',orv.CartViewset,basename="購物車")

urlpatterns = [
    path('api/token/verify/',TokenVerifyView.as_view(),name='token'),
    path('api/token/obtain/',TokenObtainPairView.as_view(),name='token'),
    path('api/token/refresh/',TokenRefreshView.as_view(),name='token'),
    path('Member/login/',dv.Member_LoginAPIViews.as_view(),name="會員登入"),
    path('Store/check/',dv.Store_LoginAPIViews.as_view(),name='店家登入'),
    path('default/admin',admin.site.urls)
]

urlpatterns += router.urls

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    # 只有在開發模式下使用static.serve視圖
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# urlpatterns = [
#     #Token
#     path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
#     path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
#     # path('admin/', admin.s ite.urls),
#     # # 登入/註冊
#     path('s/login',dv.MemberLoginAPIViews.as_view(),name='member'),
#     # path('s/register'),
#     # # 產品
#     # path('g/search'),
#     # # 個資
#     path('p/personal', dv.MemberAPIViews.as_view(),name='member'),
#     path('p/personal/pdsearch',dv.MemberP_Viewset.as_view(),name='member') ,
# ]
