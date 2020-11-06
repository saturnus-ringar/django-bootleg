from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext as _
from django_extensions.db.models import TimeStampedModel

from bootleg.db.models.base import BaseModel
from bootleg.utils import models as bootleg_models


class Profile(BaseModel, TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def to_log(self):
        return "User: [%s]" % self.user.username

    def __str__(self):
        return self.user.username

    class Meta:
        abstract = True
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile_model = bootleg_models.get_profile_model()
        if profile_model:
            profile_model.objects.create(user=instance)
