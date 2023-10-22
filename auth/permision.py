class Has_permission():
    def __init__(self) -> None:
        from django.contrib.auth.models import User, Group, Permission
    def is_store(self,props):
        from django.contrib.auth.models import User
        User.groups.check()
    def is_member(self,props):
        from django.contrib.auth.models import User