from django.db import models

# Create your models here.
from research.models import Research


class ResearchAdminProxy(Research):
    # 관리자 페이지용 research 모델 proxy
    class Meta:
        verbose_name = '연구'
        verbose_name_plural = '연구'
        proxy = True