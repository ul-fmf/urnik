from django_auth_ldap.backend import populate_user
from django.dispatch import receiver

from urnik.models import Oseba


@receiver(populate_user)
def connect_oseba_to_user(sender,  user=None, ldap_user=None, **kwargs):
    if user is None:
        return

    try:
        user.oseba
        return
    except Oseba.DoesNotExist:
        # najdemo osebo in povežemo
        pass
