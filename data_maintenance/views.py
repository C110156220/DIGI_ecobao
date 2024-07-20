from django.contrib.auth import login
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView
# from django.contrib.auth.mixins import
# 驗證密碼
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User
# 回應
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import action, permission_classes, authentication_classes
from rest_framework.status import *
from rest_framework.parsers import JSONParser
# APP內
from .serializers import *
from .models import *
# token
from rest_framework_simplejwt.views import TokenObtainPairView
# 權限
from rest_framework.permissions import IsAuthenticated, AllowAny

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
    serializer_class = Data_Member_Serializers
    queryset = Member.objects.all()

    # method -> http method , detail true -> 回傳一個物件 false -> 回傳多個物件
    @action(methods=['GET'], detail=False, permission_classes=[IsAuthenticated])
    def account(self, request):
        """
        取得會員基本的資訊 V
        """
        uid = request.user.uid
        print(uid)
        if uid == '':
            return (Response(status=404, data='未給予資料(header)'))
        if Member.objects.filter(uid_id=uid).count() != 1:
            return (Response(status=404, data="未知帳號"))
        data = Member.objects.get(uid_id=uid)
        serializer = Data_Member_Serializers(data, many=False)
        return JSONResponse(serializer.data)

    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated])
    def update_allergen(self, request):
        """
        使用者更新過敏原資料 V
        """
        uid = request.user.uid
        allergen = request.data.get('allergen', '')

        if Member.objects.filter(uid_id=uid).count() == 1:
            try:
                member_data = Member.objects.get(uid_id=uid)
                member_data.allergen = allergen
                member_data.save()
            except Exception as e:
                print(e)
                return (Response(status=500, data='系統錯誤，請洽管理'))
            return Response(status=200, data="success")
        else:
            return Response(status=404, data="未知帳號")

    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated])
    def update_account(self, request):
        """
        更新會員資料維護 V
        """
        uid = request.user.uid
        if Member.objects.filter(uid_id=uid).count() != 1:
            return (Response(status=404, data='未知帳號'))
        upd_data = {}
        upd_data['name'] = request.data.get('name', '')
        upd_data['phone'] = request.data.get('phone', '')
        upd_data['email'] = request.data.get('email', '')
        upd_data['address'] = request.data.get('address', '')
        upd_data['birth'] = request.data.get('birth', '')

        if '' in upd_data:
            return (Response(status=404, data='資料未提供完整'))

        try:
            member_data = Member.objects.get(uid_id=uid)
            member_data.name = upd_data['name']
            member_data.phone = upd_data['phone']
            member_data.email = upd_data['email']
            member_data.address = upd_data['address']
            member_data.birth = upd_data['birth']
            member_data.save()
            return Response(status=200, data='success')
        except:
            return (Response(status=404, data="資料發生重複"))

    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated])
    def delete(self, request):
        uid = request.user.uid
        if (uid == ''):
            return (Response(status=404, data='未提供資料'))
        if Member.objects.filter(uid_id=uid).count() != 1:
            return (Response(status=404, data='帳號?'))
        data1 = MemberP.objects.get(uid=uid)
        data1.is_active = 0
        data1.save()
        return Response(status=201, data="停用成功")

    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated])
    def prefer(self, request):
        uid = request.user.uid
        try:
            ob = Member.objects.get(uid=uid)
            ob.prefer = request.data.get('prefer', '')
            ob.save()
        except Member.DoesNotExist:
            return (Response(status=404, data="未知帳號"))
        return (Response(status=200, data="OK"))


class MemberP_Viewset(viewsets.ModelViewSet):
    """
    會員密碼讀取
    """
    querset = MemberP.objects.all()
    serializer_class = Data_MemberP_Serializers
    permission_class = (IsAuthenticated, AllowAny)
    parser_classes = (JSONParser,)

    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated])
    def password_upd(self, request):
        """
        使用者更新密碼
        """
        form_uid = request.user.uid
        old_pwd = request.data.get('old_password', '')
        new_pwd = request.data.get('new_password', '')
        if form_uid == '' or old_pwd == '' or new_pwd == '':
            return (Response(status=404, data='未給予資料'))
        if (MemberP.objects.filter(uid=form_uid, is_active=1).count() != 1):
            return (Response(status=404, data='未知帳號'))
        else:
            from django.contrib.auth import get_user_model
            try:
                User = get_user_model()
                data = User.objects.get(uid=form_uid)
                if check_password(old_pwd, data.password):
                    data.set_password(new_pwd)
                    data.save()
                    return (Response(status=200, data='success'))
                else:
                    return (Response(status=404, data='密碼錯誤'))
            except Exception as e:
                print(e)
                return (Response(status=500, data='出現錯誤，請洽管理'))

        # except:
        #     return Response(self.response(404,'Bad'))

    @action(methods=['post'], detail=False, permission_classes=[AllowAny])
    def forgot(self, request):
        phone = request.data.get('phone', '')
        password = request.data.get('password', '')
        if phone == '' or password == '':
            return (Response(status=400, data="參數?"))
        ob = Member.objects.filter(phone=phone)
        if ob.count() != 1:
            return (Response(status=404, data="未知帳號"))
        ob = MemberP.objects.get(uid=ob[0].uid_id)
        ob.password = make_password(password)
        ob.save()
        return (Response(status=200, data="success"))

    def response(self, status, message, result=None):
        d = {
            'status': status,
            'message': message,
            'result': result
        }
        print(d)
        if d['result'] == None:
            del d['result']
        return d


class Store_search_Viewset(viewsets.ModelViewSet):
    """
    商店功能
    """
    queryset = Store.objects.all()
    serializer_class = StoreSerializers

    @action(methods=['get'], detail=False, permission_classes=[AllowAny], authentication_classes=[])
    def all(self, request):
        """取得所有店家"""
        data = Store.objects.all()
        serializer = StoreSerializers(data, many=True)
        return JSONResponse(serializer.data)

    @action(methods=['get', 'post'], detail=False, permission_classes=[AllowAny], authentication_classes=[])
    def type(self, request):
        """取得該地區的店家"""
        type = request.GET.get('type', '')
        if type == "" or type == None:
            return Response(status=404, data="未給予搜尋的資料")
        if type == "all":
            data = Store.objects.all()
        else:
            data = Store.objects.filter(type=request.GET.get('type', ''))
        serializer = StoreSerializers(data, many=True)
        return JSONResponse(serializer.data)

    @action(methods=['get'], detail=False, permission_classes=[AllowAny], authentication_classes=[])
    def prefer(self, request):
        import random
        try:
            uid = request.user.uid
            ob = Member.objects.filter(uid=uid)
            login = True
        except Member.DoesNotExist:
            return (Response(status=404, data="未知帳號"))
        except AttributeError:
            login = False
        except Exception as e :
            print(e);login = False

        if login:
            if ob[0].prefer == None or ob[0].prefer == '':
                res = Store.objects.all().order_by('?')[:10]
            else:
                l = eval(ob[0].prefer)
                try:
                    res = Store.objects.filter(type__in=l).order_by('?')[:12]
                except Store.DoesNotExist:
                    return (Response(status=404, data="未找到任何條件"))
        else:
            res = Store.objects.all().order_by('?')[:10]

        ser = StoreSerializers(res,many=True)
        return (Response(status=200, data=ser.data))

    @action(methods=['get', 'post'], detail=False, permission_classes=[AllowAny], authentication_classes=[])
    def area(self, request):
        """前端給予"條件"進行搜尋"""
        if request.data.get('name') == "" or request.data.get('name') == None:
            return Response(status=404, data="未給予搜尋的資料(店家姓名)")
        if request.data.get('area') == "":
            return Response(status=404, data="未給予搜尋的資料(地區)")
        data = Store.objects.filter(
            name__contains=request.data.get('name'),
            area=request.data.get('area')
        )
        serializer = StoreSerializers(data, many=True)
        return JSONResponse(serializer.data)

    @action(methods=['get', 'post'], detail=False, permission_classes=[AllowAny], authentication_classes=[])
    def search(self, request):
        if request.GET.get('name', '') == '' or request.GET.get('name', '') == None:
            return (Response(status=404, data='沒輸入資料喔'))
        try:
            data = Store.objects.filter(
                name__contains=request.GET.get('name')
            )
            serializer = StoreSerializers(data, many=True)
            return JSONResponse(serializer.data)
        except:
            return Response(status=500, data="出問題搂")

    @action(methods=['get', 'post'], detail=False, permission_classes=[AllowAny], authentication_classes=[])
    def device_around(self, request):
        from geopy.distance import geodesic
        lat = request.data.get('lat', '0')
        lng = request.data.get('lng', '0')
        device_location = (float(lat), float(lng))
        meter = 5000
        all_data = Store.objects.all()
        serializer = StoreSerializers(all_data, many=True)
        res = []
        km = 5
        for i in serializer.data:
            if geodesic(device_location, (i['lat'], i['lng'])) <= km:
                res.append(i)
        return JSONResponse(res)

    @action(methods=['GET'], detail=False, permission_classes=[AllowAny], authentication_classes=[])
    def score(self, request):
        """
        透過前端給予ID，進行查詢
        """
        from goods import models
        sid = request.GET.get('sid', '')
        try:
            sid = Store.objects.get(sid=sid)
        except Store.DoesNotExist:
            return (Response(status=404, data="未知商家"))
        from django.db.models import Sum
        import math
        try:
            total_score_for_sid = models.Evaluate.objects.filter(sid=sid).aggregate(
                total_score=Sum('star'))['total_score']/models.Evaluate.objects.filter(sid=sid).count()
            return (Response(status=200, data={'rating': math.floor(total_score_for_sid)}))
        except:
            return (Response(status=200, data={'rating': 0}))

    @action(methods=['get'], detail=False, permission_classes=[AllowAny], authentication_classes=[])
    def id(self, request):
        """取得該ID的店家"""
        try:
            data = Store.objects.filter(sid=request.GET.get('sid'))
            serializer = StoreSerializers(data, many=True)
            return JSONResponse(serializer.data)
        except Store.DoesNotExist:
            return (Response(status=404, data="未知店家"))

    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated])
    def chge_data(self, request):
        data = Store.objects.get(sid=request.POST['id'])
        data.type = request.post['type']
        data.name = request.post['name']
        data.intro = request.post['intro']
        data.address = request.post['address']
        return Response(data=data, status=HTTP_200_OK)

    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated])
    def chge_address(self, request):
        data = Store.objects.get(sid=request.POST['id'])
        return Response(data=data, status=HTTP_200_OK)

    # 內部
    def response(self, status, message, result=None):
        d = {
            'status': status,
            'message': message,
            'result': result
        }
        print(d)
        if d['result'] == None:
            del d['result']
        return d


# 店家資訊
class Store_data_Viewset(viewsets.ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializers

    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated])
    def food(self, request):
        from goods.models import Goods
        from goods.serializers import Goods_serializers
        uid = request.user.uid
        goods = Goods.objects.filter(sid_id=uid)
        serializer = Goods_serializers(goods, many=True)
        return (Response(status=200, data=serializer.data))

    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated])
    def score(self, request):
        from goods import models
        sid = request.user.uid
        try:
            sid = Store.objects.get(upid=sid)
        except Store.DoesNotExist:
            return (Response(status=404, data="商家未知"))

        from django.db.models import Sum
        import math
        try:
            total_score_for_sid = models.Evaluate.objects.filter(sid=sid).aggregate(
                total_score=Sum('star'))['total_score']/models.Evaluate.objects.filter(sid=sid).count()
            return (Response(status=200, data={'rating': math.floor(total_score_for_sid)}))
        except:
            return (Response(status=200, data={'rating': 1}))

    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated])
    def get(self, request):
        uid = request.user.uid
        ob = Store.objects.filter(upid_id=uid)
        serializer = StoreSerializers(ob, many=True)
        return (Response(status=200, data=serializer.data))

    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated])
    def register(self, request):
        """初步註冊"""
        uid = request.user.uid
        if uid == "" or uid == None:
            return Response(status=400, data="資料未給予")
        memob = MemberP.objects.filter(uid=uid)
        if (memob.count() != 1):
            return Response(status=400, data="account not found")
        if Store.objects.filter(upid=uid).count() == 1:
            return (Response(status=400, data="已經註冊搂!"))
        data = {}
        data['type'] = request.data.get('type', '')
        data['name'] = request.data.get('name', '')
        data['email'] = request.data.get('email', '')
        data['phone'] = request.data.get('phone')
        data['address'] = request.data.get('address', '')
        try:
            pic = request.data.get('pic', '')
            if pic != '':
                image_data = PicSave(pic, 'Store')
            else:
                image_data = pic

        except Exception as e:
            print(e)
            print('pic not upload')

        print(data['address'])
        data['on_business'] = False
        area = data['address'].split('區')[0]
        if "市" in data['address']:
            city = data['address'].split('市')[0]
            data['city'] = city[-2:]
        elif "縣" in data['address']:
            city = data['address'].split('縣')[0]
            data['city'] = city[-2:]
        data['area'] = area[-2:]
        google_data = self.__getlatlng(data['address'])
        if google_data:
            data['lng'] = google_data['lng']
            data['lat'] = google_data['lat']
            if self.__new_account(data, uid, image_data):
                return Response(status=200, data="success")
            else:
                return Response(status=500, data="新增失敗，請洽系統管理")
        else:
            return (Response(status=400, data="地址未找到任何記錄"))

    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated])
    def close(self, request):
        uid = request.user.uid
        if Member.objects.filter(uid=uid).count() != 1:
            return (Response(status=404, data="帳號?"))
        try:
            ob = Store.objects.get(upid=uid)
            ob.status = False
            return (Response(status=HTTP_202_ACCEPTED, data="success"))
        except Store.DoesNotExist:
            return (Response(status=400, data="店家?"))

    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated])
    def change(self, request):
        uid = request.user.uid
        if uid == "" or uid == None:
            return Response(status=400, data="資料未給予")
        if (MemberP.objects.filter(uid=uid).count() != 1):
            return Response(status=400, data="account not found")
        try:
            pic = request.data.get('pic', '')
            if pic != '':
                image_data = PicSave(pic,'Store')
            else:
                image_data = pic
        except:
            print('照片未傳送')

        try:
            from django.core.files.base import ContentFile
            ob = Store.objects.get(upid=uid)
            ob.intro = request.data.get('intro', '')
            ob.pic = image_data
            ob.link_fb = request.data.get('link_fb', '')
            ob.link_ig = request.data.get('link_ig', '')
            ob.on_business = request.data.get('on_business', True)
            ob.save()
            return (Response(status=200, data="success"))
        except Store.DoesNotExist:
            return (Response(status=404, data="店家未知"))

    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated])
    def Eva(self, request):
        sid = request.user.uid
        print(sid)
        try:
            from goods.models import Evaluate
            from goods.serializers import Evaluate_serializers
            uid = Store.objects.get(upid_id=sid)
            ob = Evaluate.objects.filter(sid=uid)
            data = Evaluate_serializers(ob, many=True)
            if data.data == []:
                return (Response(status=200, data="無資料"))
            else:
                return (Response(status=200, data=data.data))
        except Member.DoesNotExist:
            return (Response(status=404, data="非會員"))
        except Store.DoesNotExist:
            return (Response(status=404, data="非店家"))
        except Exception as e:
            print(e)
            return (Response(status=500, data=e))

    # in
    def __new_account(self, dict, member_obj, image=None):
        from django.core.files.base import ContentFile
        try:
            sid = "S{0:08d}".format(Store.objects.all().count()+3)
            new_ob = Store(
                sid=sid,
                upid_id=member_obj,
                type=dict['type'],
                name=dict['name'],
                # intro = dict['intro'],
                city=dict['city'],
                area=dict['area'],
                address=dict['address'],
                lng=dict['lng'],
                lat=dict['lat'],
                pic=image,
                phone=dict['phone'],
                email=dict['email'],
                # link = dict['link'],
                on_business=dict['on_business']
            )
            new_ob.save()
            return True
        except Exception as e:
            print(e)
            return False

    def __getlatlng(self, address=''):
        import requests
        if address == '':
            return (print('未輸入地址'))
        # 定義Google Maps Geocoding API的網址
        geocoding_api_url = "https://maps.googleapis.com/maps/api/geocode/json"
        # 製作請求的參數
        params = {
            'address': address,
            'key': "User_input!"
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
            return ({'address': formatted_address, 'lat': latitude, 'lng': longitude})
        else:
            print('未能拿到資料，程式碼錯誤?')
            print(data)
            return (False)


# 會員登入


class Member_LoginAPIViews(TokenObtainPairView):
    """會員登入"""
    serializer_class = Data_MemberP_Serializers
    permission_classes = [AllowAny]
    parser_classes = [JSONParser,]

    @login_required
    def post(self, request, *args, **kwargs):
        try:
            user = request.user
            account = request.data.get('account')
            password = request.data.get('password')
            mb = authenticate(request, account=account, password=password)
            if mb:
                user = request.user
                login(request, user)
                token = super().post(request, *args, **kwargs)
                return (Response(status=200, data=token))
            else:
                return (Response(status=404, data="帳號密碼錯誤"))
            # 调用原始的 TokenObtainPairView 的 post 方法获取令牌
        except Exception as e:
            return (Response(status=500, data="系統發生錯誤{}".format(e)))

# 店家驗證


class Store_LoginAPIViews(APIView):
    serializer_class = StoreSerializers
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser,]

    def get(self, request):
        user1 = request.user.uid
        user = Member.objects.filter(uid_id=user1)
        if user.count() != 1:
            return Response(status=400, data="未知帳號")
        try:
            ob = Store.objects.filter(upid_id=user1)
            if ob.count() == 1:
                return (Response(status=200, data="歡迎{}，請繼續提供美味的食物！".format(ob[0].name)))
        except Store.DoesNotExist:
            return (Response(status=404, data="用戶未註冊商家"))

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

    @action(methods=['post'], detail=False, permission_classes=[AllowAny],authentication_classes=[])
    def new(self, request):
        # 驗證資料
        data = {}
        data['name'] = (request.data.get('name', ''))
        data['phone'] = (request.data.get('phone', ''))
        data['gender'] = (request.data.get('gender', ''))
        data['email'] = (request.data.get('email', ''))
        data['address'] = (request.data.get('address', ''))
        data['birth'] = (request.data.get('birth', ''))
        data['allergen'] = (request.data.get('allergen', ''))

        data2 = {}
        data2['account'] = request.data.get('account', '')
        data2['password'] = request.data.get('password', '')

        if '' in data or None in data:
            return (Response(status=404, data='未提供資料'))
        if '' in data2 or None in data2:
            return (Response(status=404, data='未提供資料'))
        if MemberP.objects.filter(account=data2['account']).count() == 1:
            return (Response(status=404, data='帳號重複'))
        # 測試用
        if self.__new_private(data2, data):
            return (Response(status=200, data='success'))
        # if self.__new_account(data,data2):
        #     return(Response(status=200,data='success'))
        else:
            return (Response(status=500, data='會員建置系統錯誤，確認資料是否有誤'))

    def __new_account(self, uid, dict1):
        try:
            # uid = "M{0:08d}".format(Member.objects.all().count() + 2)
            new_ob = Member(
                uid_id=uid,
                name=dict1['name'],
                phone=dict1['phone'],
                gender=dict1['gender'],
                email=dict1['email'],
                address=dict1['address'],
                birth=dict1['birth'],
                allergen=dict1['allergen'],
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

    def __new_private(self, dict, dict2):
        from django.contrib.auth import get_user_model
        from django.contrib.auth.models import Group
        try:
            user = get_user_model()
            uid = "M{0:05d}".format(Member.objects.count() + 3)
            user.objects.create_user(
                uid=uid,
                account=dict['account'],
                password=dict['password'],
                is_active=True,
                is_staff=False,
                is_superuser=False)

            if self.__new_account(uid, dict2):
                return True
            else:
                print('會員資料建置有誤')
                return False
        except Exception as e:
            print(e)
            return False


def PicSave(decodetext, target):
    from PIL import Image
    import base64
    import uuid
    import os
    from django.core.files.base import ContentFile
    from ecobao.settings import MEDIA_ROOT
    # 將Base64數據解碼
    try:
        image_data = base64.b64decode(decodetext.split(',')[1])
    except base64.binascii.Error:
        return ("base64 error")
    # 創建文件對象
    try:
        # 在media目錄下創建一個唯一的文件名，或者使用您自己的文件命名邏輯
        file_name = str(uuid.uuid4())
        img_url = os.path.join(
            MEDIA_ROOT, '{}/{}.png'.format(target, file_name))
        # address = '/assets/{}/{}.png'.format(target,file_name)
        image_file = ContentFile(image_data, name="{}.png".format(file_name))
        # with open(img_url,'wb') as f:
        #     f.write(image_data)
        return image_file
    except Exception as e:
        print("Error in creating Image file -> {}".format(e))
        return False
