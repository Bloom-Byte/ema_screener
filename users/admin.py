from django.contrib import admin

from .models import UserAccount, PasswordResetToken


admin.site.register(UserAccount)
admin.site.register(PasswordResetToken)
