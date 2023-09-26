from django.contrib.auth.models import Permission

permission = Permission.objects.create(
    codename='view_dashboard',
    name='Can view dashboard',
    content_type=content_type_object,  # 设置相应的内容类型对象
)
