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
                result = [research.project_title, participate.participate_at, participate.participant.email,
                          participate.participant.name, participate.agree_date, participategame.game.game_title, participategame.finished_dt,
                          participategame.result.rt, participategame.result.stimulus, participategame.result.trial_type,
                          participategame.result.trial_index, participategame.result.time_elapsed, participategame.result.button_pressed,
                          participategame.result.internal_node_id]
                ws.append(result)
        dirname = os.path.join(settings.BASE_DIR, settings.MEDIA_ROOT, 'cache', '%Y', "{}.xlsx".format(research.project_title))
        wb.save(dirname)
        return serve(request, dirname)


