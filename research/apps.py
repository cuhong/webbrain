from django.apps import AppConfig


class ResearchConfig(AppConfig):
    name = 'research'
    verbose_name = '연구관리'

    def ready(self):
        from research.signals import research_post_save
