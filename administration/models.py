from django.db import models

# Create your models here.
from solo.models import SingletonModel

from research.models import Research


class ResearchAdminProxy(Research):
    # 관리자 페이지용 research 모델 proxy
    class Meta:
        verbose_name = '연구'
        verbose_name_plural = '연구'
        proxy = True


class MainPage(SingletonModel):
    modified_at = models.DateTimeField(auto_now=True, verbose_name='최종 수정일')
    doc = models.TextField(null=True, blank=True, verbose_name='메인페이지')

    def __str__(self):
        return '메인페이지'
    class Meta:
        verbose_name = 'main page'