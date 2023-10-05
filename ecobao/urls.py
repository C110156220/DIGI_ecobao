"""ecobao URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from data_maintenance.serializers import Member_TokenObtainPairSerializer
from django.contrib import admin
from django.urls import path
import data_maintenance.views as dv
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
# router.register(r'', dv.Member_LoginAPIViews,basename='member')
# router.register(r'accounts', AccountViewSet)

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
