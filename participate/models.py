from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import JSONField
from django.db import models

User = get_user_model()


class Participate(models.Model):
    class Meta:
        unique_together = (('participant', 'research'))
        verbose_name = '연구참여자'
        verbose_name_plural = verbose_name

    participate_at = models.DateTimeField(auto_now_add=True, verbose_name='연구시작일시')
    participant = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, verbose_name='참가자')
    research = models.ForeignKey('research.Research', on_delete=models.CASCADE, null=False, blank=False, verbose_name='연구')
    agree = models.BooleanField(default=False, verbose_name='동의')
    agree_name = models.CharField(max_length=100, null=True, blank=False, verbose_name='동의자명')
    agree_date = models.DateField(null=True, blank=False, verbose_name='동의일')
    is_finish = models.BooleanField(default=False, verbose_name='완료여부')


class ParticipateGameList(models.Model):
    class Meta:
        unique_together = ('participate', 'game')
        verbose_name = '게임결과'
        verbose_name_plural = verbose_name

    participate = models.ForeignKey(Participate, on_delete=models.CASCADE)
    game = models.ForeignKey('research.Game', on_delete=models.CASCADE, verbose_name='게임')
    finished_dt = models.DateTimeField(auto_now_add=True, verbose_name='참여일시')
    result = JSONField(null=True, blank=True, verbose_name='결과')


