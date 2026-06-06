from django.db import models
from django.utils.translation import gettext_lazy as _

class Branch(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Branch Name"))
    location = models.CharField(max_length=255, verbose_name=_("Location / Address"))
    phone = models.CharField(max_length=20, verbose_name=_("Phone Number"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Branch")
        verbose_name_plural = _("Branches")