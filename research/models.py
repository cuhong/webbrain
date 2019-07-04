import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from ordered_model.models import OrderedModel
from taggit.managers import TaggableManager

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
    project_end_date = models.DateField(null=False, blank=False, verbose_name='연구 종료일')
    project_agreement = models.TextField(null=False, blank=False, verbose_name='연구동의서')
    reward = models.BooleanField(default=False, verbose_name='리워드 제공')
    reward_description = models.CharField(max_length=300, null=True, blank=True, verbose_name='리워드 내용')
    tags = TaggableManager(verbose_name='태그', blank=True)
    agree_name = models.BooleanField(default=False, verbose_name='개인정보수집 동의 요구(성명)')
    agree_tel = models.BooleanField(default=False, verbose_name='개인정보수집 동의 요구(전화번호)')
    agree_gender = models.BooleanField(default=False, verbose_name='개인정보수집 동의 요구(성별)')
    agree_email = models.BooleanField(default=False, verbose_name='개인정보수집 동의 요구(이메일)')
    agree_age = models.BooleanField(default=False, verbose_name='개인정보수집 동의 요구(연령)')
    condition_age_min = models.PositiveIntegerField(null=True, blank=True, verbose_name='연구참여조건(나이 하한)')
    condition_age_max = models.PositiveIntegerField(null=True, blank=True, verbose_name='연구참여조건(나이 상한)')
    condition_gender = models.IntegerField(choices=CONDITION_GENDER_CHOICES, default=0, verbose_name='연구참여조건(성별)')

    status = models.IntegerField(choices=STATUS_CHOICES, default=0, null=False, blank=False, verbose_name='상태')

    def __str__(self):
        return self.project_title

    def clean(self):
        if self.project_start_date > self.project_end_date:
            raise ValidationError("연구 종료일은 연구 시작일 이전일 수 없습니다.")
        if self.condition_age_max or self.condition_age_min:
            if not self.agree_age:
                raise ValidationError("연구참여조건에 나이가 있으나 개인정보 수집 동의 요구를 하지 않았습니다.")
        if not self.condition_gender == 0:
            if not self.agree_gender:
                raise ValidationError("연구참여조건에 성별이 있으나 개인정보 수집 동의 요구를 하지 않았습니다.")
        if self.reward:
            if self.agree_email or self.agree_tel:
                pass
            else:
                raise ValidationError("리워드 제공건임에도 불구하고 전화번호 혹은 이메일 수집 동의 요구를 하지 않았습니다.")
            if not self.reward_description:
                raise ValidationError("리워드 제공건임에도 불구하고 리워드 내용을 입력하지 않았습니다.")

        super(Research, self).clean()

    @property
    def is_open(self):
        """
        연구의 승인여부와, 시작/종료일 확인 후 True/False 반환
        """
        if not self.status == 2:
            return False
        today = timezone.localdate()
        if today <= self.project_end_date and today >= self.project_start_date:
            return True
        return False


class ResearchAdminProxyForResearch(Research):
    # 연구원 페이지용 research 모델 proxy
    class Meta:
        verbose_name = '연구'
        verbose_name_plural = '연구'
        proxy = True


class Game(OrderedModel):
    class Meta(OrderedModel.Meta):
        ordering = ('research', 'order')

    order = models.PositiveIntegerField(verbose_name='순서', editable=False, db_index=True)

    registered_at = models.DateTimeField(auto_now_add=True)
    research = models.ForeignKey(ResearchAdminProxyForResearch, on_delete=models.PROTECT, verbose_name='연구', editable=False)
    game_title = models.CharField(max_length=300, null=False, blank=False, verbose_name='게임명')
    game_file = models.FileField(null=False, blank=False, verbose_name='게임파일', upload_to='project/game/%Y/%m/%d')
    order_with_respect_to = 'research'


class ResearchAdminProxy(Research):
    # 관리자 페이지용 research 모델 proxy
    class Meta:
        verbose_name = '연구'
        verbose_name_plural = '연구'
        proxy = True