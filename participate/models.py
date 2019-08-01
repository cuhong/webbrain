from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import JSONField
from django.db import models
from solo.models import SingletonModel

User = get_user_model()


class MainPage(SingletonModel):
    modified_at = models.DateTimeField(auto_now=True, verbose_name='최종 수정일')
    doc = models.TextField(null=True, blank=True, verbose_name='메인페이지')

    def __str__(self):
        return '메인페이지'
    class Meta:
        verbose_name = 'main page'



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

    def calculate_score(self):
        try:
            score_list = []
            rt_list = []
            result = self.result
            main_seq = self.game.game_json['sequences']['main_sequence']
            for idx, seq in enumerate(main_seq):
                answer = seq.get('answer', None)
                if answer:
                    if result[idx]['button_pressed'] == answer:
                        score_list.append(True)
                    else:
                        score_list.append(False)

                rt = result[idx].get('rt', None)
                if rt:
                    rt_list.append(rt)

            result = {'score': {'correct': score_list.count(True), 'count': len(score_list)}, 'avg_rt': sum(rt_list)/len(rt_list)/1000}
        except:
            result = {'score': {'correct': 0, 'count': 0}, 'avg_rt': 0}
        return result




