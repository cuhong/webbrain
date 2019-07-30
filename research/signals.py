import shutil

import zipfile
import os

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from research.models import Game, Research
from administration.models import ResearchAdminProxy
from research.parsers import Parser


@receiver(post_save, sender=Game)
def game_post_save(sender, instance, created, raw, using, **kwargs):
    if created:
        with zipfile.ZipFile(instance.game_file.path, 'r') as zip:
            zip.extractall(instance.game_file.path.split('.')[0])

        parsed_dict = Parser(instance.exp_path)
        instance.game_json = parsed_dict.parsed_dict
        instance.save()