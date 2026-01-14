from django.db import models


class TimedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UserOwnedModel(models.Model):
    user = models.ForeignKey("userdata.User", on_delete=models.CASCADE)

    class Meta:
        abstract = True
