import shutil

import zipfile
import os

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from research.models import Game, Research, ResearchAdminProxy


@receiver(post_save, sender=Game)
def game_post_save(sender, instance, created, raw, using, **kwargs):
    path = instance._game_path
    with zipfile.ZipFile(instance.game_file.path, 'r') as zip:
        zip.extractall(path)
    instance.game_path = path