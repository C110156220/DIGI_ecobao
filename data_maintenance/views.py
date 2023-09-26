from django.core import serializers
from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView
# 驗證密碼
from django.contrib.auth.hashers import make_password,check_password
# from rest_framework.generics import get_object_or_404
# 回應
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import action,permission_classes
from rest_framework.status import *
from rest_framework.parsers import JSONParser
from rest_framework import generics
from rest_framework import mixins
from .serializers import *
from .models import *

#權限
from rest_framework.permissions import IsAuthenticated
# JSON 格式輸出'
class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


# 會員View

class MemberAPIViews(viewsets.ModelViewSet):
    """
    會員基本功能
    """
    @action(methods=['get'], detail=False)
    @permission_classes([IsAuthenticated])
    # method -> http method , detail true -> 回傳一個物件 false -> 回傳多個物件
    def get_account(self,request):
        """
        取得會員基本的資訊
        """
        data = Member.objects.get(account = request.POST['account'])
        data = serializers.serialize('json',data)
        return Response(data,status=HTTP_200_OK)

    @action(methods=['post'], detail=False)
    @permission_classes([IsAuthenticated])
    def update_allergen(self,request):
        """
        使用者更新過敏原來源
        """
        member_data = Member.objects.get(uid = id)
        member_data.allergen = request.POST['allergen']
        member_data.save()
        return Response(HTTP_202_ACCEPTED)
    @action(methods=['post'], detail=False)
    @permission_classes([IsAuthenticated])
    def update_account_data(self,request):
        """
        更新會員資料維護
        """
        member_data = Member.objects.get(uid = id)
        member_data.name = request.POST['name']
        member_data.phone = request.POST['phone']
        member_data.gender = request.POST['gender']
        member_data.email = request.POST['email']
        member_data.address = request.POST['address']
        member_data.birth = request.POST['birth']
        member_data.save()
        return Response(HTTP_202_ACCEPTED)
    @action(methods=['post'], detail=False)
    def new_account(self,request):
        """
        註冊帳號
        """
        thisid =  Member.objects.count()+1
        ob1 = Member.objects.create(
            uid = thisid,
            name = request.POST['name'],
            phone = request.POST['phone'],
            gender = request.POST['gender'],
            email = request.POST['email'],
            address = request.POST['address'],
            birth = request.POST['birth'],
            allergen = request.POST['allergen']
        )
        ob1.save()
        ob2 = MemberP.objects.create(
            upid_id = thisid,
            account = request.POST['account'],
            password = make_password(request.POST['password'])
        )
        ob2.save()
        return(Response(HTTP_201_CREATED))
    @action(methods=['get'], detail=False)
    @permission_classes([IsAuthenticated])
    def delete_account(self,request):
        data = Member.objects.get(uid = request.POST['uid'])
        data.delete()
        return Response()

class MemberP_Viewset(viewsets.ModelViewSet):
    """
    會員密碼讀取
    """
    querset = MemberP.objects.all()
    serializer_class = Data_MemberP_Serializers
    permission_class = (IsAuthenticated,)
    parser_classes = (JSONParser,)


    @action(methods=['post'], detail=False)
    def update_password(self,request):
        """
        使用者更新密碼
        """
        data = MemberP.objects.get(account =request.POST['account'])
        data.password = request.POST['request']
        data.save()
        return (Response(HTTP_202_ACCEPTED))
        # except:
        #     return Response(self.response(404,'Bad'))
    def response(self,status,message,result=None):
        d = {
            'status' : status,
            'message' : message,
            'result' : result
        }
        print(d)
        if d['result'] == None :
            del d['result']
        return d

class Store_search_Viewset(viewsets.ModelViewSet):
    """
    商店功能
    """
    @action(methods=['get'], detail=False)
    def get_stores(self,request):
        """取得所有店家"""
        data = Store.objects.all()
        serializer = StoreSerializers(data,many=True)
        return JSONResponse(serializer.data)

    @action(methods=['get'], detail=False)
    def get_area_stores(self,request):
        """取得該地區的店家"""
        if request.data.get('area') == "" or request.data.get('area') == None:
            return Response(status=404,data="未給予搜尋的資料")
        data = Store.objects.filter(area = request.data.get('area',''))
        serializer = StoreSerializers(data,many=True)
        return JSONResponse(serializer.data)
    @action(methods=['get'], detail=False)
    def search_area_store(self,request):
        """前端給予"條件"進行搜尋"""
        if request.data.get('name') == "" or request.data.get('name') == None:
            return Response(status=404,data="未給予搜尋的資料(名稱)")
        if request.data.get('area') == "":
            return Response(status=404,data="未給予搜尋的資料(地區)")
        data = Store.objects.filter(
            name__contains = request.data.get('name'),
            area = request.data.get('area')
        )
        serializer = StoreSerializers(data,many=True)
        return JSONResponse(serializer.data)
    @action(methods=['get'], detail=False)
    def search(self,request):
        try:
            data = Store.objects.filter(
                name__contains = request.data.get('name')
            )
            serializer = StoreSerializers(data,many=True)
            return JSONResponse(serializer.data)
        except:
            return Response(status=500,data = "出問題搂")
        
    @action(method=['get'],detail=False)
    def get_store_device_loc(self,request):
        lat = request.data.get('lat')
        lng = request.data.get('lng')



    @action(methods=['get'], detail=False)
    def get_id_store(self,request):
        """取得該ID的店家"""
        data = Store.objects.get(sid = request.data.get('sid'))
        serializer = StoreSerializers(data,many=True)
        return JSONResponse(serializer.data)

    @action(methods=['post'], detail=False)
    def chge_data(self,request):
        data = Store.objects.get(sid = request.POST['id'])
        data.type = request.post['type']
        data.name = request.post['name']
        data.intro = request.post['intro']
        data.address = request.post['address']
        return Response(data=data,status=HTTP_200_OK)

    @action(methods=['post'], detail=False)
    def chge_address(self,request):
        data = Store.objects.get(sid = request.POST['id'])
        return Response(data=data,status=HTTP_200_OK)

    # 內部
    def response(self,status,message,result=None):
        d = {
            'status' : status,
            'message' : message,
            'result' : result
        }
        print(d)
        if d['result'] == None :
            del d['result']
        return d

class Store_data_Viewset(viewsets.ModelViewSet):

    @action(methods=['get'], detail=False)
    def get_stores(self,request):
        """取得所有店家"""
        data = Store.objects.all()
        serializer = StoreSerializers(data,many=True)
        return JSONResponse(serializer.data)


# 登入
class Member_LoginAPIViews(APIView):
    def post(self,request):
        """
        登入
        """
        from django.contrib.auth import authenticate
        from rest_framework_simplejwt.tokens import RefreshToken
        try:
            data = request.data
            serializer = LoginSerializers(data=data)
            if serializer.is_valid():
                account = serializer.data['account']
                password = serializer.data['password']
                user = authenticate(
                    account = account,
                    password = password
                    )
                if user is None :
                    return(Response(status=HTTP_404_NOT_FOUND,data={'message':'not found'}))
                refresh_token = RefreshToken.for_user(user=user)
                return(Response(status=HTTP_200_OK,data={'refresh':str(refresh_token),'access':str(refresh_token.access_token)}))
        except:
            pass
        # account = request.POST.get('account')
        # form_password = request.POST.get('password')
        # data_password = MemberP.objects.get(account = account)
        # serializer = Data_MemberP_Serializers(data_password)
        # if check_password(form_password,serializer.data['password']):
        #     return Response(status=HTTP_200_OK)
        # else:
        #     return Response(status=HTTP_404_NOT_FOUND)
# 註冊
@permission_classes([])
class Member_registerAPIViews(APIView):
    def post(self,request):
        a = request.POST['account']
        p = request.POST['password']
        # try :
        ob = MemberP.objects.create(
            account = a , password = p
            )
        ob.save()
#
class EmployeeLoginAPIViews(APIView):
    def post(self,request):
        account = request.POST.get('account')
        form_password = request.POST.get('password')
        data_password = EmployeeP.objects.get(account = account)
        serializer = Data_MemberP_Serializers(data_password)
        if check_password(form_password,serializer.data['password']):
            return Response(status=HTTP_200_OK)
        else:
            return Response(status=HTTP_404_NOT_FOUND)