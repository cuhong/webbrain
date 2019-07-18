from django.apps import AppConfig


class ParticipateConfig(AppConfig):
    name = 'participate'

    def ready(self):
        from participate.signals import participate_post_save
