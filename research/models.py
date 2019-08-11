import os
import uuid

from django.contrib.postgres.fields import JSONField
from django.core.validators import FileExtensionValidator
from django.db import models
from ordered_model.models import OrderedModel
from taggit.managers import TaggableManager

from participate.models import Participate, ParticipateGameList
from users.models import CustomUser


def uuid_hex():
    u = uuid.uuid4()
    return u.hex


class Research(models.Model):
    class Meta:
        verbose_name = '연구'
        verbose_name_plural = '연구'

    STATUS_CHOICES = ((0, '기타'), (1, '대기'), (2, '연구중'), (3, '일시정지'), (4, '연구종료'), (5, '블럭'))
    CONDITION_GENDER_CHOICES = ((0, '성별무관'), (1, '남성'), (2, '여성'))
    registered_at = models.DateTimeField(auto_now_add=True)
    hex = models.UUIDField(default=uuid.uuid4, null=False, verbose_name='연구 고유키', unique=True)
    user = models.ForeignKey(CustomUser, on_delete=models.PROTECT, verbose_name='연구자')
    project_title = models.CharField(max_length=300, null=False, blank=False, verbose_name='프로젝트 이름',
                                     help_text='300자 미만 입력')
    project_description = models.TextField(null=False, blank=False, verbose_name='프로젝트 설명')
    project_start_date = models.DateField(null=False, blank=False, verbose_name='연구 시작일')
    project_agreement = models.TextField(null=False, blank=False, verbose_name='연구동의서')
    reward = models.BooleanField(default=False, verbose_name='리워드 제공')
    reward_description = models.CharField(max_length=300, null=True, blank=True, verbose_name='리워드 내용')
    tags = TaggableManager(verbose_name='태그', blank=True)
    condition_age_min = models.PositiveIntegerField(null=True, blank=True, verbose_name='연구참여조건(나이 하한)')
    condition_age_max = models.PositiveIntegerField(null=True, blank=True, verbose_name='연구참여조건(나이 상한)')
    condition_gender = models.IntegerField(choices=CONDITION_GENDER_CHOICES, default=0, verbose_name='연구참여조건(성별)')

    status = models.IntegerField(choices=STATUS_CHOICES, default=1, null=False, blank=False, verbose_name='상태')

    def __str__(self):
        return self.project_title


class Agree(models.Model):
    class Meta:
        verbose_name = '동의'
        verbose_name_plural = verbose_name

    research = models.ForeignKey(Research, null=False, blank=False, verbose_name='연구', on_delete=models.PROTECT)
    item = models.CharField(max_length=300, null=False, blank=False, verbose_name='동의 조건')

    def __str__(self):
        return self.item


class Game(OrderedModel):
    class Meta(OrderedModel.Meta):
        ordering = ('research', 'order')

    order = models.PositiveIntegerField(verbose_name='순서', db_index=True)
    registered_at = models.DateTimeField(auto_now_add=True)
    research = models.ForeignKey(Research, on_delete=models.PROTECT, verbose_name='연구', editable=False)
    game_title = models.CharField(max_length=300, null=False, blank=False, verbose_name='게임명')
    game_file = models.FileField(null=False, blank=False, verbose_name='게임파일', upload_to='project/game/%Y/%m/%d',
                                 validators=[FileExtensionValidator(allowed_extensions=['zip'])])
    game_json = JSONField(null=True, blank=True, verbose_name='게임 json')
    parse_result = models.BooleanField(default=False, verbose_name='파싱성공')
    order_with_respect_to = 'research'

    @property
    def _game_path(self):
        return self.game_file.path.split('.')[0]

    @property
    def _game_media_url(self):
        return self.game_file.url[0:self.game_file.url.rfind('.')]

    @property
    def exp_path(self):
        return os.path.join(self._game_path, 'exp.txt')

    def __str__(self):
        return self.game_title


class ResearchAdminProxyForResearch(Research):
    # 연구원 페이지용 research 모델 proxy
    class Meta:
        verbose_name = '연구'
        verbose_name_plural = '연구'
        proxy = True


class ParticipateAdminProxy(Participate):
    # 연구원 페이지용 Participate 모델 proxy
    class Meta:
        verbose_name = '연구참여자'
        verbose_name_plural = '연구참여자'
        proxy = True


class ParticipateGameListAdminProxy(ParticipateGameList):
    # 연구원 페이지용 ParticipateGameList 모델 proxy
    class Meta:
        verbose_name = '게임결과'
        verbose_name_plural = '게임결과'
        proxy = True
