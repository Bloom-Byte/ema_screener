from django.contrib import admin

from .models import AuthToken, PasswordResetToken


admin.site.register(AuthToken)
admin.site.register(PasswordResetToken)
