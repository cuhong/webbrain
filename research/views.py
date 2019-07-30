import os

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.staticfiles.views import serve
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views import View

from participate.models import Participate
from research.models import Research


class ResearchResultDownloadView(LoginRequiredMixin, View):
    def get(self, request, research_hex):
        from openpyxl import Workbook
        research = get_object_or_404(Research, Q(user=request.user) & Q(hex=research_hex))
        participate_list = Participate.objects.prefetch_related('participategamelist_set', 'participategamelist_set__game').filter(research=research)
        wb = Workbook()
        ws = wb.active
        for participate in participate_list:
            for participategame in participate.participategamelist_set.all():
                result_base = [research.project_title, participate.participate_at, participate.participant.email,
                          participate.participant.name, participate.agree_date, participategame.game.game_title, participategame.finished_dt]
                for line in participategame.result:
                    result_base += [line['rt'], line['stimulus'], line['trial_type'], line['trial_index'],
                                    line['time_elapsed'], line['button_pressed'], line['internal_node_id']]
                    ws.append(result_base)
        dirname = os.path.join(settings.BASE_DIR, settings.MEDIA_ROOT, 'cache', '%Y', "{}.xlsx".format(research.project_title))
        wb.save(dirname)
        return serve(request, dirname)


