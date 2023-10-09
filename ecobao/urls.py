from django.contrib import admin
from django.urls import path

# app.Views
import data_maintenance.views as dv
import goods.views as goodv
import activity.views as actv
# router settings
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = routers.SimpleRouter()
router.register(r'member', dv.MemberAPIViews,basename='member')
router.register(r'memberP',dv.MemberP_Viewset,basename='memberp')
router.register(r'store_data', dv.Store_data_Viewset,basename='store')
router.register(r'store_sch',dv.Store_search_Viewset,basename='Store_search')
router.register(r'register',dv.Member_register_APIViews,basename='register')
router.register(r'Goods',goodv.Goods_Viewset,basename='good')
router.register(r'store_data/goods',goodv.Goods_Upload_Viewsets,basename='Store_data_aboutGoods')
router.register(r'news',actv.Activity_Get_APIViews,basename='news')
router.register(r'Evaluate',goodv.Evaluate_store_Viewset,basename='評論')

urlpatterns = [
    path('api/token/obtain/',TokenObtainPairView.as_view(),name='token'),
    path('api/token/refresh/',TokenRefreshView.as_view(),name='token'),
    path('Member/login/',dv.Member_LoginAPIViews.as_view(),name="login"),
    path('default/admin',admin.site.urls)
]

urlpatterns += router.urls



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
