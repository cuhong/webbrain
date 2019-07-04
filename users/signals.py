import shutil

from django.contrib.auth.models import Permission
from django.db.models.signals import post_save
from django.dispatch import receiver

from users.models import CustomUser, ResearcherUser


@receiver(post_save, sender=ResearcherUser)
def researcheruser_post_save(sender, instance, created, raw, using, **kwargs):
    if created:
        if instance.is_researcher:
            permissions = Permission.objects.filter(codename__icontains='researchadminproxyforresearch')
            instance.user_permissions.set(permissions)
            instance.save()
