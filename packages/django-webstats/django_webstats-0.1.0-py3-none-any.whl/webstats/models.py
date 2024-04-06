from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class Visit(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    url_path = models.URLField()
    view_name = models.CharField(max_length=255, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    def __str__(self):
        return f"{self.url_path} at {self.created} by {self.ip_address}"
