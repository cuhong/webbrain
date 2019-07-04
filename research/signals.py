import shutil

from django.db.models.signals import post_save
from django.dispatch import receiver

from research.models import Game, Research


@receiver(post_save, sender=Research)
def research_post_save(sender, instance, created, raw, using, **kwargs):

    import zipfile
    import os
    from webbrain.settings import BASE_DIR
    game_list = Game.objects.filter(research=instance)
    game_file_list = [[game.id, game.game_file.path] for game in game_list]
    research_id = instance.id
    path_base = os.path.join(BASE_DIR, 'media', 'game_extracted', str(research_id))
    for file in game_file_list:
        _path = os.path.join(path_base, str(file[0]))
        if os.path.exists(_path):
            shutil.rmtree(_path)
        with zipfile.ZipFile(file[1], 'r') as zip:
            zip.extractall(_path)
