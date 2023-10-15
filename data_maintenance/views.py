from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView
# 驗證密碼
from django.contrib.auth.hashers import make_password,check_password
from django.contrib.auth.models import User
# 回應
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import action,permission_classes,authentication_classes
from rest_framework.status import *
from rest_framework.parsers import JSONParser
# APP內
from .serializers import *
from .models import *
# token
from rest_framework_simplejwt.views import TokenObtainPairView
#權限
from rest_framework.permissions import IsAuthenticated,AllowAny

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
    serializer_class=Data_Member_Serializers
    queryset = Member.objects.all()

    # method -> http method , detail true -> 回傳一個物件 false -> 回傳多個物件
    @action(methods=['GET'], detail=False,permission_classes=[IsAuthenticated])
    def account(self,request):
        """
        取得會員基本的資訊 V
        """
        uid = request.user.uid
        print(uid)
        if uid == '':
            return (Response(status=404,data='未給予資料(header)'))
        if Member.objects.filter(uid_id=uid).count() != 1:
            return(Response(status=404,data="未知帳號"))
        data = Member.objects.get(uid_id = uid)
        serializer = Data_Member_Serializers(data,many = False)
        return JSONResponse(serializer.data)

    @action(methods=['post'], detail=False,permission_classes=[IsAuthenticated])
    def update_allergen(self,request):
        """
        使用者更新過敏原資料 V
        """
        uid = request.user.uid
        allergen = request.data.get('allergen','')

        if Member.objects.filter(uid_id = uid).count() == 1:
            try:
                member_data = Member.objects.get(uid_id = uid)
                member_data.allergen = allergen
                member_data.save()
            except Exception as e:
                print(e)
                return(Response(status=500,data='系統錯誤，請洽管理'))
            return Response(status=200,data="success")
        else:
            return Response(status=404,data="未知帳號")

    @action(methods=['post'], detail=False,permission_classes = [IsAuthenticated])
    def update_account(self,request):
        """
        更新會員資料維護 V
        """
        uid = request.user.uid
        if Member.objects.filter(uid_id=uid).count() != 1:
            return(Response(status=404,data='未知帳號'))
        upd_data = {}
        upd_data['name'] = request.data.get('name','')
        upd_data['phone'] =request.data.get('phone','')
        upd_data['email'] = request.data.get('email','')
        upd_data['address'] = request.data.get('address','')
        upd_data['birth'] = request.data.get('birth','')

        if '' in upd_data : return(Response(status=404,data='資料未提供完整'))

        try:
            member_data = Member.objects.get(uid_id = uid)
            member_data.name = upd_data['name']
            member_data.phone = upd_data['phone']
            member_data.email = upd_data['email']
            member_data.address = upd_data['address']
            member_data.birth = upd_data['birth']
            member_data.save()
            return Response(status=200,data='success')
        except:
            return(Response(status=404,data="資料發生重複"))

    @action(methods=['post'], detail=False,permission_classes = [IsAuthenticated])
    def delete(self,request):
        uid = request.user.uid
        if (uid == ''):
            return(Response(status=404,data='未提供資料'))
        if Member.objects.filter(uid_id=uid).count() != 1 :
            return(Response(status=404,data='帳號?'))
        data1 = MemberP.objects.get(uid=uid)
        data1.is_active = 0
        data1.save()
        return Response(status=201,data="停用成功")

class MemberP_Viewset(viewsets.ModelViewSet):
    """
    會員密碼讀取
    """
    querset = MemberP.objects.all()
    serializer_class = Data_MemberP_Serializers
    permission_class = (IsAuthenticated,AllowAny)
    parser_classes = (JSONParser,)


    @action(methods=['post'], detail=False,permission_classes = [IsAuthenticated])
    def password_upd(self,request):
        """
        使用者更新密碼
        """
        form_uid = request.user.uid
        old_pwd = request.data.get('old_password','')
        new_pwd = request.data.get('new_password','')
        if form_uid == '' or old_pwd == '' or new_pwd == '' :
            return(Response(status=404,data='未給予資料'))
        if (MemberP.objects.filter(uid = form_uid,is_active=1).count() != 1):
            return(Response(status=404,data='未知帳號'))
        else:
            from django.contrib.auth import get_user_model
            try:
                User = get_user_model()
                data = User.objects.get(uid = form_uid)
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

    @action(methods=['post'], detail=False,permission_classes=[AllowAny])
    def forgot(self,request):
        phone = request.data.get('phone','')
        password = request.data.get('password','')
        if phone == '' or password == '':
            return(Response(status=400,data="參數?"))
        ob = Member.objects.filter(phone=phone)
        if ob.count() != 1 :
            return(Response(status=404,data="未知帳號"))
        ob = MemberP.objects.get(uid = ob[0].uid_id)
        ob.password = make_password(password)
        ob.save()
        return(Response(status=200,data="success"))

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

    @action(methods=['get'], detail=False,permission_classes=[AllowAny],authentication_classes=[])
    def all(self,request):
        """取得所有店家"""
        data = Store.objects.all()
        serializer = StoreSerializers(data,many=True)
        return JSONResponse(serializer.data)

    @action(methods=['get','post'], detail=False,permission_classes = [AllowAny],authentication_classes=[])
    def type(self,request):
        """取得該地區的店家"""
        if request.GET.get('type','') == "" or request.GET.get('type','') == None:
            return Response(status=404,data="未給予搜尋的資料")
        data = Store.objects.filter(type = request.GET.get('type',''))
        serializer = StoreSerializers(data,many=True)
        return JSONResponse(serializer.data)

    @action(methods=['get','post'], detail=False,permission_classes=[AllowAny],authentication_classes=[])
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

    @action(methods=['get','post'], detail=False ,permission_classes=[AllowAny],authentication_classes=[])
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

    @action(methods=['get','post'],detail=False,permission_classes=[AllowAny],authentication_classes=[])
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
    @action(methods=['GET'],detail=False,permission_classes=[AllowAny],authentication_classes=[])
    def score(self,request):
        from goods import models
        sid = request.GET.get('sid','')
        if sid == '':
            return(res().dataError())
        sid = Store.objects.get(sid=sid)
        from django.db.models import Sum
        import math
        total_score_for_sid = models.Evaluate.objects.filter(sid=sid).aggregate(total_score=Sum('star'))['total_score']/models.Evaluate.objects.filter(sid=sid).count()
        return(Response(status=200,data={'rating':math.floor(total_score_for_sid)}))

    @action(methods=['get'], detail=False,permission_classes=[AllowAny],authentication_classes=[])
    def id(self,request):
        """取得該ID的店家"""
        try:
            data = Store.objects.filter(sid = request.GET.get('sid'))
            serializer = StoreSerializers(data,many=True)
            return JSONResponse(serializer.data)
        except Store.DoesNotExist:
            return(Response(status=404,data="未知店家"))


    @action(methods=['post'], detail=False,permission_classes=[IsAuthenticated])
    def chge_data(self,request):
        data = Store.objects.get(sid = request.POST['id'])
        data.type = request.post['type']
        data.name = request.post['name']
        data.intro = request.post['intro']
        data.address = request.post['address']
        return Response(data=data,status=HTTP_200_OK)

    @action(methods=['post'], detail=False,permission_classes=[IsAuthenticated])
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

    @action(methods=['post'] , detail=False ,permission_classes=[IsAuthenticated])
    def register(self,request):
        """初步註冊"""
        uid = request.user.uid
        if uid == "" or uid == None :
            return Response(status=400,data="資料未給予")
        memob = MemberP.objects.filter(uid = request.data.get('uid'))
        if (memob.count() != 1):
            return Response(status=400,data="account not found")
        if Store.objects.filter(upid=memob).count() == 1:
            return(Response(status=HTTP_203_NON_AUTHORITATIVE_INFORMATION,data="已經註冊搂!"))
        data = {}
        data['name'] = request.data.get('name','')
        data['intro'] = request.data.get('intro','')
        data['area'] = request.data.get('area','')
        data['address'] = request.data.get('address','')
        data['link'] = request.data.get('link','')
        data['on_business'] = request.data.get('on_business',False)

        google_data = self.__getlatlng(data['address'])
        if google_data:
            data['lng'] = google_data['lng']
            data['lat'] = google_data['lat']
            account_info = MemberP.objects.get(uid = uid)
            if self.__new_account(data,account_info):
                return Response(status=200,data="success")
            else:
                return Response(status=500,data="新增失敗，請洽系統管理")
        else:
            return(Response(status=400,data="地址未找到任何記錄"))

    @action(methods=['get'],detail = False,permission_classes=[IsAuthenticated])
    def delit(self,request):
        pass
    # @action(methods=['post'],detail= False)

    @action(methods=['post'] , detail=False,permission_classes=[IsAuthenticated])
    def upd(self,request):
        uid = request.user.uid
        if uid == "" or uid == None :
            return Response(status=400,data="資料未給予")
        if (MemberP.objects.filter(uid = request.data.get('uid')).count() != 1):
            return Response(status=400,data="account not found")
        # 資料驗證
        data = {}
        data['type'] = request.data.get('type','')
        data['name'] = request.data.get('name','')
        data['intro'] = request.data.get('intro','')
        data['area'] = request.data.get('area','')
        data['address'] = request.data.get('address','')
        data['lng'] = request.data.get('lng','')
        data['lat'] = request.data.get('lat','')
        data['link'] = request.data.get('link','')
        data['on_business'] = request.data.get('on_business','')

            # if '' in data or None in data :
            #     return Response(status=404,data='未給予資料')

        if (MemberP.objects.filter(uid = data['upid']).count() != 1):
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

    def __getlatlng(address = ''):
        import requests
        if address == '':
            return(print('未輸入地址'))
        # 定義Google Maps Geocoding API的網址
        geocoding_api_url = "https://maps.googleapis.com/maps/api/geocode/json"
        # 製作請求的參數
        params = {
            'address': address,
            'key':'AIzaSyAmDnwpBu8Vr5pNEetVPt0qfsEXwa54bFw'
        }
        # 發送GET請求
        response = requests.get(geocoding_api_url, params=params)
        # 解析回應的JSON數據
        data = response.json()
        # 檢查是否成功獲取經緯度
        if data['status'] == 'OK':
            result = data['results'][0]
            formatted_address = result['formatted_address']
            location = result['geometry']['location']
            latitude = location['lat']
            longitude = location['lng']
            return({'address':formatted_address,'lat':latitude,'lng':longitude})
        else:
            print('未能拿到資料，程式碼錯誤?')
            print(data)
            return(False)




# 會員登入
class Member_LoginAPIViews(APIView):
    serializer_class = Data_MemberP_Serializers
    permission_classes = [AllowAny]
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
# 店家驗證
class Store_LoginAPIViews(APIView):
    @action(methods=['get'],detail=False,permission_classes=[IsAuthenticated],)
    def switch(self,request):
        user = request.user.uid
        user = Member.objects.filter(uid_id = user)
        if user.count() != 1 :
            return Response(status=400,data="未知帳號")
        try:
            ob = Store.objects.filter(upid_id = user)
            if ob.count() == 1:
                return(Response(status=200,data="歡迎{}，請繼續提供美味的食物！".format(ob[0].name)))
        except Store.DoesNotExist:
            return(Response(status=404,data="用戶未註冊商家"))

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
    serializer_class = Data_Member_Serializers
    queryset = Member.objects.all()

    @action(methods=['post'],detail= False,permission_classes=[AllowAny])
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
        from django.contrib.auth.models import Group
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