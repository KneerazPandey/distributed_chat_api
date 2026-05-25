from django.contrib import admin
from apps.accounts.models import User, SocialAccount, Profile


admin.site.register(User)
admin.site.register(SocialAccount)
admin.site.register(Profile)
