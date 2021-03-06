from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import JSONField
from django.db import models
from solo.models import SingletonModel

User = get_user_model()
import json

from django.contrib.postgres.forms.jsonb import (
    InvalidJSONInput,
    JSONField as JSONFormField,
)


class UTF8JSONFormField(JSONFormField):

    def prepare_value(self, value):
        if isinstance(value, InvalidJSONInput):
            return value
        return json.dumps(value, ensure_ascii=False)


class UTF8JSONField(JSONField):
    """JSONField for postgres databases.

    Displays UTF-8 characters directly in the admin, i.e. äöü instead of
    unicode escape sequences.
    """

    def formfield(self, **kwargs):
        return super().formfield(**{
            **{'form_class': UTF8JSONFormField},
            **kwargs,
        })


class Participate(models.Model):
    class Meta:
        unique_together = (('participant', 'research'))
        verbose_name = '연구참여자'
        verbose_name_plural = verbose_name

    participate_at = models.DateTimeField(auto_now_add=True, verbose_name='연구시작일시')
    participant = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, verbose_name='참가자',
                                    editable=False)
    research = models.ForeignKey('research.Research', on_delete=models.CASCADE, null=False, blank=False,
                                 verbose_name='연구', editable=False)
    agree = models.BooleanField(default=False, verbose_name='동의', editable=False)
    agree_name = models.CharField(max_length=100, null=True, blank=False, verbose_name='동의자명')
    poll = UTF8JSONField(null=True, blank=True, verbose_name='설문결과')

    def __str__(self):
        return "[{}] {}".format(self.participant, self.research)


class ParticipateGameList(models.Model):
    class Meta:
        verbose_name = '게임결과'
        verbose_name_plural = verbose_name

    participate = models.ForeignKey(Participate, on_delete=models.CASCADE, editable=False)
    game = models.ForeignKey('research.Game', on_delete=models.CASCADE, verbose_name='게임', editable=False)
    finished_dt = models.DateTimeField(auto_now_add=True, verbose_name='참여일시', editable=False)
    result = JSONField(null=True, blank=True, verbose_name='결과', editable=False)
    count = models.IntegerField(null=True, blank=True, verbose_name='문항수')
    correct = models.IntegerField(null=True, blank=True, verbose_name='정답')
    response_time = models.FloatField(null=True, blank=True, verbose_name='평균응답시간')

    def __str__(self):
        return "[{}] {}/{}".format(self.participate.participant, self.participate.research, self.game.game_title)

    def calculate_score(self):
        score_list = []
        rt_list = []
        result_list = self.result
        for result in result_list:
            rt = result.get('rt', None)
            if rt:
                rt_list.append(rt)
            correct_response = result.get('correct_response', None)
            if correct_response:  # 정답이 있고

                _button_pressed = result.get('button_pressed', None)
                if _button_pressed:
                    button_pressed = int(_button_pressed)
                    if button_pressed == int(correct_response):
                        score_list.append(True)
                    else:
                        score_list.append(False)
                else:  # 정답을 미선택한 경우
                    score_list.append(False)
            else:
                continue
        try:
            result = {'score': {'correct': score_list.count(True), 'count': len(score_list)},
                      'avg_rt': sum(rt_list) / len(rt_list) / 1000}
        except ZeroDivisionError:
            result = {'score': {'correct': score_list.count(True), 'count': len(score_list)},
                      'avg_rt': 0}

        self.count = len(score_list)
        self.correct = score_list.count(True)
        if len(rt_list) != 0:
            self.response_time = sum(rt_list) / len(rt_list) / 1000
        self.save()
        return result
