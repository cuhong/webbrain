import shutil

from django.contrib.auth.models import Permission
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver

from users.models import CustomUser, ResearcherUser, StaffUser, ParticipantUser

from functools import wraps


def skip_signal():
    def _skip_signal(signal_func):
        @wraps(signal_func)
        def _decorator(sender, instance, **kwargs):
            if hasattr(instance, 'skip_signal'):
                return None
            return signal_func(sender, instance, **kwargs)

        return _decorator

    return _skip_signal


def get_researcher_permission():
    models = ['researchadminproxyforresearch', 'game', 'agree', 'participate', 'patricipategamelist']
    q = Q()
    for model in models:
        q |= Q(codename__icontains=model)
    permissions = Permission.objects.filter(q)
    return permissions


def get_admin_permission():
    all_permissions = Permission.objects.all()
    return all_permissions


def set_permission(instance):
    research_permissions = get_researcher_permission()
    admin_permissions = get_admin_permission()
    _perm = instance.user_permissions
    if instance.is_researcher:
        for perm in research_permissions:
            _perm.add(perm)
    else:
        for perm in research_permissions:
            _perm.remove(perm)

    if instance.is_staff:
        for perm in admin_permissions:
            _perm.add(perm)
    else:
        for perm in admin_permissions:
            _perm.remove(perm)


def researcheruser_post_save(sender, instance, created, raw, using, **kwargs):
    research_permissions = get_researcher_permission()
    admin_permissions = get_admin_permission()
    user = CustomUser.objects.get(id=instance.id)
    if instance.is_researcher:
        for perm in research_permissions:
            user.user_permissions.add(perm)
    else:
        for perm in research_permissions:
            user.user_permissions.remove(perm)

    if instance.is_staff:
        for perm in admin_permissions:
            user.user_permissions.add(perm)
    else:
        for perm in admin_permissions:
            user.user_permissions.remove(perm)
    user.save()


def staffuser_post_save(sender, instance, created, raw, using, **kwargs):
    research_permissions = get_researcher_permission()
    admin_permissions = get_admin_permission()
    user = CustomUser.objects.get(id=instance.id)
    if instance.is_researcher:
        for perm in research_permissions:
            user.user_permissions.add(perm)
    else:
        for perm in research_permissions:
            user.user_permissions.remove(perm)

    if instance.is_staff:
        for perm in admin_permissions:
            user.user_permissions.add(perm)
    else:
        for perm in admin_permissions:
            user.user_permissions.remove(perm)
    user.save()



def participateuser_post_save(sender, instance, created, raw, using, **kwargs):
    research_permissions = get_researcher_permission()
    admin_permissions = get_admin_permission()
    user = CustomUser.objects.get(id=instance.id)
    if instance.is_researcher:
        for perm in research_permissions:
            user.user_permissions.add(perm)
    else:
        for perm in research_permissions:
            user.user_permissions.remove(perm)

    if instance.is_staff:
        for perm in admin_permissions:
            user.user_permissions.add(perm)
    else:
        for perm in admin_permissions:
            user.user_permissions.remove(perm)
    user.save()
