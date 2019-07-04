from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = 'users'
    verbose_name = '사용자'

    def ready(self):
        from users.signals import researcheruser_post_save