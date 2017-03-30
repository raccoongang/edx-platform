from django.db import models


class TokenStorage(models.Model):
    secret_token = models.UUIDField(null=True)
