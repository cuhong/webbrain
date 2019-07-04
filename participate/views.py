from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.views import View
from django.views.generic import TemplateView

from research.models import Research


class ParticipateView(TemplateView):
    template_name = 'agree.html'


    def get_context_data(self, **kwargs):
        context = super(ParticipateView, self).get_context_data(**kwargs)
        research_hex = self.kwargs['research_hex']
        context['research'] = get_object_or_404(Research, hex=research_hex)
        return context
