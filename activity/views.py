# Model About Member
from django.contrib.auth.models import User
# Return need
from rest_framework.response import Response
from django.http import HttpResponse
from django.http import JsonResponse
# APIViews
from rest_framework import viewsets
from django_ratelimit.decorators import ratelimit
from rest_framework.decorators import action,permission_classes
#  權限
from rest_framework.permissions import IsAuthenticated,AllowAny
# JSON ABOUT
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
# model
from .models import Activity
# seri
from .serializers import Activity_serializers




class Activity_Get_APIViews(viewsets.ModelViewSet):
    serializer_class = Activity_serializers
    queryset = Activity.objects.all()

    @action(methods=['get'],permission_classes=[AllowAny],detail=False)
    # @ratelimit(key='ip', rate='8/m', method='ALL', block=True)
    def all(self,request):
        """取得所有文章"""
        article = Activity.objects.filter(status=True)
        serializer = Activity_serializers(article,many=True)
        return(JsonResponse(serializer.data,safe=False))

    @action(methods=['get'],permission_classes=[AllowAny],detail=False)
    # @ratelimit(key='ip', rate='8/m', method='ALL', block=True)
    def one(self,request):
        """取得該ID的文章"""
        actid = request.GET.get('actid','')
        if actid == "": return(Response(status=404,data="資料?"))
        if Activity.objects.filter(actid = actid).count() != 1 :
            return(Response(status=404,data="不會叫你去Google"))

        article = Activity.objects.filter(actid = actid)
        serializer = Activity_serializers(article,many=True)
        return(JsonResponse(serializer.data,safe=False))


class Activity_Edit_APIViews(viewsets.ModelViewSet):
    serializer_class = Activity_serializers
    queryset = Activity.objects.all()

    @action(methods=['post'],permission_classes=[IsAuthenticated],detail=False)
    def edit(self,request):
        """編輯特定文章"""
        article_id = request.data.get('actid')
        if Activity.objects.filter(actid = article_id).count() != 1:
            return(Response(status=404,data="編輯失敗，未知文章"))
        form_data = request.data
        try:
            new_acticle = Activity.objects.get(actid = article_id)
            new_acticle.title = form_data['title']
            new_acticle.author = form_data['author']
            new_acticle.upload_date = form_data['upload_date']
            new_acticle.down_date = form_data['down_date']
            new_acticle.content = form_data['content']
            new_acticle.status = form_data['status']
            new_acticle.pic1 = form_data.get('pic1','')
            new_acticle.pic2 = form_data.get('pic2','')
            new_acticle.pic3 = form_data.get('pic3','')
            new_acticle.save()
            return(Response(status=200,data='success'))
        except Exception as e :
            return(Response(status=404,data={'error':'儲存錯誤','message':e}))