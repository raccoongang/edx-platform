from django.contrib import admin
from .models import TokenStorage


class TokenStorageAdmin(admin.ModelAdmin):
    """
    Admin for token`s storage.
    """
    fields = ['secret_token']

admin.site.register(TokenStorage, TokenStorageAdmin)
