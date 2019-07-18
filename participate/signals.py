import shutil

import zipfile
import os

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from participate.models import Participate, ParticipateGameList
from research.models import Game


@receiver(post_save, sender=Participate)
def participate_post_save(sender, instance, created, raw, using, **kwargs):
    research = instance.research
    games = Game.objects.filter(research=research)
    for game in games:
        g, created = ParticipateGameList.objects.get_or_create(participate=instance, game=game)