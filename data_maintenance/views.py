from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView
# 驗證密碼
from django.contrib.auth.hashers import make_password,check_password
from django.contrib.auth.models import User
# 回應
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import action,permission_classes
from rest_framework.status import *
from rest_framework.parsers import JSONParser
# APP內
from .serializers import *
from .models import *
# token
from rest_framework_simplejwt.views import TokenObtainPairView
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

# Token
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = Member_TokenObtainPairSerializer
# 會員View

class MemberAPIViews(viewsets.ModelViewSet):
    """
    (登入後_會員功能)
    """
    @action(methods=['get'], detail=False)
    @permission_classes([IsAuthenticated])
    # method -> http method , detail true -> 回傳一個物件 false -> 回傳多個物件
    def account(self,request):
        """
        取得會員基本的資訊
        """
        uid = request.data.get('uid','')
        if uid == '':
            return (Response(status=404,data='未提供資料'))

        data = Member.objects.get(uid_id = request.data.get('uid'))
        data = Data_Member_Serializers(data,many = True)
        return JSONResponse(data)

    @action(methods=['post'], detail=False)
    @permission_classes([IsAuthenticated])
    def update_allergen(self,request):
        """
        使用者更新過敏原來源
        """
        uid = request.user.user_id
        allergen = request.data.get('allergen','')
        if uid == '' or allergen == '':return(Response(status=404,data='未提供資料'))
        if Member.objects.filter(uid_id = uid).count() == 1:
            try:
                member_data = Member.objects.get(uid = request.data.get('uid'))
                member_data.allergen = allergen
                member_data.save()
            except Exception as e:
                print(e)
                return(Response(status=500,data='系統錯誤，請洽管理'))
        return Response(HTTP_202_ACCEPTED)

    @action(methods=['post'], detail=False)
    @permission_classes([IsAuthenticated])
    def update_account(self,request):
        """
        更新會員資料維護
        """
        upd_data = {}
        upd_data['name'] = request.data.get('name','')
        upd_data['phone'] =request.data.get('phone','')
        upd_data['gender'] = request.data.get('gender','')
        upd_data['email'] = request.data.get('email','')
        upd_data['address'] = request.data.get('address','')
        upd_data['birth'] = request.data.get('birth','')

        if '' in upd_data : return(Response(status=404,data='資料未提供完整'))

        member_data = Member.objects.get(uid = id)
        member_data.name = upd_data['name']
        member_data.phone = upd_data['phone']
        member_data.gender = upd_data['gender']
        member_data.email = upd_data['email']
        member_data.address = upd_data['address']
        member_data.birth = upd_data['birth']
        member_data.save()
        return Response(status=200,data='success')


    @action(methods=['post'], detail=False)
    @permission_classes([IsAuthenticated])
    def delete(self,request):
        uid = request.data.get('uid')
        if (uid == ''):
            return(Response(status=404,data='未提供資料'))
        if Member.objects.filter(uid=uid) != 1 :
            return(Response(status=404,data='帳號?'))

        data = Member.objects.get(uid = request.data.get('uid'))
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
    def password_upd(self,request):
        """
        使用者更新密碼
        """
        form_account = request.data.get('account','')
        old_pwd = request.data.get('old_password','')
        new_pwd = request.data.get('new_password','')
        if form_account == '' or old_pwd == '' or new_pwd == '' :
            return(Response(status=404,data='未給予資料'))
        if (MemberP.objects.filter(account = form_account).count() != 1):
            return(Response(status=404,data='未知帳號'))
        else:
            from django.contrib.auth import get_user_model
            try:
                User = get_user_model()
                data = User.objects.get(account =request.data.get('account'))
                if check_password(old_pwd,data.password):
                    data.set_password(new_pwd)
                    data.save()
                    return (Response(status=200,data='success'))
                else:
                    return(Response(status=404,data='密碼錯誤'))
            except Exception as e :
                print(e)
                return (Response(status=500,data='出現錯誤，請洽管理'))


        # except:
        #     return Response(self.response(404,'Bad'))

    @action(methods=['post'], detail=False)
    def forgot(self,request):
        pass

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
    queryset = Store.objects.all()
    serializer_class = StoreSerializers

    @action(methods=['get'], detail=False)
    def all(self,request):
        """取得所有店家"""
        data = Store.objects.all()
        serializer = StoreSerializers(data,many=True)
        return JSONResponse(serializer.data)

    @action(methods=['get','post','options'], detail=False)
    def type(self,request):
        """取得該地區的店家"""
        if request.GET.get('type','') == "" or request.GET.get('type','') == None:
            return Response(status=404,data="未給予搜尋的資料")
        data = Store.objects.filter(type = request.GET.get('type',''))
        serializer = StoreSerializers(data,many=True)
        return JSONResponse(serializer.data)

    @action(methods=['get','post'], detail=False)
    def area(self,request):
        """前端給予"條件"進行搜尋"""
        if request.data.get('name') == "" or request.data.get('name') == None:
            return Response(status=404,data="未給予搜尋的資料(店家姓名)")
        if request.data.get('area') == "":
            return Response(status=404,data="未給予搜尋的資料(地區)")
        data = Store.objects.filter(
            name__contains = request.data.get('name'),
            area = request.data.get('area')
        )
        serializer = StoreSerializers(data,many=True)
        return JSONResponse(serializer.data)

    @action(methods=['get','post'], detail=False)
    def search(self,request):
        if request.GET.get('name','') == '' or request.GET.get('name','') == None:
            return(Response(status=404,data='沒輸入資料喔'))
        try:
            data = Store.objects.filter(
                name__contains = request.GET.get('name')
            )
            serializer = StoreSerializers(data,many=True)
            return JSONResponse(serializer.data)
        except:
            return Response(status=500,data = "出問題搂")

    @action(methods=['get','post'],detail=False)
    def device_around(self,request):
        from geopy.distance import geodesic
        lat = request.data.get('lat','0')
        lng = request.data.get('lng','0')
        device_location = (float(lat),float(lng))
        meter = 1000
        all_data = Store.objects.all()
        serializer = StoreSerializers(all_data,many = True)
        res = []
        km = 5
        for i in serializer.data:
            if geodesic(device_location,(i['lat'],i['lng'])) <=km :
                res.append(i)
        return JSONResponse(res)

    @action(methods=['get'], detail=False)
    def id(self,request):
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


#店家資訊
class Store_data_Viewset(viewsets.ModelViewSet):
    querysets = Store.objects.all()
    serializer_class = StoreSerializers

    @action(methods=['post'] , detail=False)
    def register(self,request):
        uid = request.data.get('uid','')
        if uid == "" or uid == None :
            return Response(status=404,data="資料未給予")

        data = {}
        data['name'] = request.data.get('name','')
        data['intro'] = request.data.get('intro','')
        data['area'] = request.data.get('area','')
        data['address'] = request.data.get('address','')
        data['lng'] = request.data.get('lng','')
        data['lat'] = request.data.get('lat','')
        data['link'] = request.data.get('link','')
        data['on_business'] = request.data.get('on_business','')

        if (Member.objects.filter(uid_id = request.data.get('uid')).count() == 1):
            return Response(status=404,data="account not found")

        account_info = Member.objects.get(uid = request.data.get('uid'))

        if self.__new_account(data,account_info):
            return Response(status=200,data="success")
        else:
            return Response(status=404,data="請洽系統管理")
    @action(methods=['get'],detail = False)
    def delit(self,request):
        pass
    # @action(methods=['post'],detail= False)

    @action(methods=['post'] , detail=False)
    def upd(self,request):
        # 資料驗證
        data = {}
        data['sid'] = request.data.get('sid','')
        data['upid'] = request.data.get('upid','')
        data['type'] = request.data.get('type','')
        data['name'] = request.data.get('name','')
        data['intro'] = request.data.get('intro','')
        data['area'] = request.data.get('area','')
        data['address'] = request.data.get('address','')
        data['lng'] = request.data.get('lng','')
        data['lat'] = request.data.get('lat','')
        data['link'] = request.data.get('link','')
        data['on_business'] = request.data.get('on_business','')

        if '' in data or None in data :
            return Response(status=404,data='未給予資料')

        if (Member.objects.filter(uid = data['upid']).count() == 1):
            return Response(status=404,data="account not found")

        upd_data = Store.objects.get(sid = data['sid'])
        upd_data.type = data['type']
        upd_data.name = data['name']
        upd_data.intro =  data['intro']
        upd_data.area = data['area']
        upd_data.address = data['address']
        upd_data.lng = data['lng']
        upd_data.lat = data['lat']
        upd_data.link = data['link']
        upd_data.on_business = data['on_business']
        upd_data.save()


    # in
    def __new_account(self,dict,member_obj):
        try:
            sid = "S{0:08d}".format(Store.objects.get('sid'))
            new_ob = Store(
                sid = sid ,
                upid = member_obj,
                type = dict['type'],
                name = dict['name'],
                intro = dict['intro'],
                area = dict['area'],
                address = dict['address'],
                lng = dict['lng'],
                lat = dict['lat'],
                link = dict['link'],
                on_business = dict['on_business']
            )
            new_ob.save()
            return True
        except Exception as e:
            print(e)
            return False




# 會員登入
class Member_LoginAPIViews(APIView):
    serializer_class = Data_MemberP_Serializers
    parser_classes = [JSONParser,]
    def post(self,request):
        form_account = request.data.get('account')
        form_password = request.data.get('password')
        db_data = MemberP.objects.filter(account = form_account)
        if db_data.count() != 1:
            return Response(status=404,data='帳號密碼錯誤')
        db_object = MemberP.objects.get(account = form_account)
        if check_password(form_password,db_data[0].password) :
            token = MyTokenObtainPairView.get_token(db_object)
            parse_token = {
            'refresh': str(token),
            'access': str(token.access_token),
        }
            return(Response(status=201,data=parse_token))
        else:
            return(Response(status=404,data='帳號密碼錯誤'))


# #
# class EmployeeLoginAPIViews(APIView):
#     def post(self,request):
#         account = request.POST.get('account')
#         form_password = request.POST.get('password')
#         data_password = EmployeeP.objects.get(account = account)
#         serializer = Data_MemberP_Serializers(data_password)
#         if check_password(form_password,serializer.data['password']):
#             return Response(status=HTTP_200_OK)
#         else:
#             return Response(status=HTTP_404_NOT_FOUND)


# 註冊
class Member_register_APIViews(viewsets.ModelViewSet):
    # serializer_class = Data_Member_Serializers

    @action(methods=['post'],detail= False)
    def new(self,request):
        # 驗證資料
        data = {}
        data['name'] =(request.data.get('name',''))
        data['phone'] =(request.data.get('phone',''))
        data['gender'] =(request.data.get('gender',''))
        data['email'] =(request.data.get('email',''))
        data['address'] =(request.data.get('address',''))
        data['birth'] =(request.data.get('birth',''))
        data['allergen'] =(request.data.get('allergen',''))

        data2 ={}
        data2['account'] = request.data.get('account','')
        data2['password'] = request.data.get('password','')

        if '' in data or None in data :
            return(Response(status=404,data='未提供資料'))
        if '' in data2 or None in data2 :
            return(Response(status=404,data='未提供資料'))
        if MemberP.objects.filter(account = data2['account']).count() == 1:
            return (Response(status=404,data='帳號重複'))
        # 測試用
        if self.__new_private(data2,data):
            return (Response(status=200,data='success'))
        # if self.__new_account(data,data2):
        #     return(Response(status=200,data='success'))
        else :
            return(Response(status=500,data='會員建置系統錯誤，確認資料是否有誤'))

    def __new_account(self,uid,dict1):
        try:
            # uid = "M{0:08d}".format(Member.objects.all().count() + 2)
            new_ob = Member(
                uid_id = uid,
                name = dict1['name'],
                phone = dict1['phone'],
                gender = dict1['gender'],
                email = dict1['email'],
                address = dict1['address'],
                birth = dict1['birth'],
                allergen = dict1['allergen'],
            )
            new_ob.save()
            return True
        except Exception as e:
            print(e)
            return False
        #     if self.__new_private(dict2,new_ob):
        #         return True
        #     else:
        #         return False
        # except Exception as e:
        #     print('error in normal')
        #     print(e)
        #     return False

    def __new_private(self,dict,dict2):
        from django.contrib.auth import get_user_model
        try:
            user = get_user_model()
            uid = "M{0:05d}".format(Member.objects.count() +3)
            user.objects.create_user(
                uid = uid,
                account=dict['account'],
                password=dict['password'],
                is_active=True,
                is_staff =False,
                is_superuser=False)
            if self.__new_account(uid,dict2):
                return True
            else:
                print('會員資料建置有誤')
                return False
        except Exception as e:
            print(e)
            return False


#