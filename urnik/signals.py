from django_auth_ldap.backend import populate_user
from django.dispatch import receiver

from urnik.models import Oseba


@receiver(populate_user)
def connect_oseba_to_user(sender,  user=None, ldap_user=None, **kwargs):
    if user is None:
        return
    user.save()
    try:
        user.oseba
        return
    except Oseba.DoesNotExist:
        if not user.first_name or not user.last_name:
            return
        osebe = list(Oseba.objects.filter(ime=user.first_name, priimek=user.last_name, user__isnull=True))
        if not osebe:
            oseba = Oseba(ime=user.first_name, priimek=user.last_name)
        else:
            oseba = osebe[0]

        oseba.user = user
        oseba.email = user.email
        oseba.save()
