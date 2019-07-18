from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView

from participate.models import Participate, ParticipateGameList
from research.models import Research, Game
from django import forms

class NameDateForm(forms.Form):

    name = forms.CharField()
    date = forms.DateField(input_formats=['%Y-%m-%d'])


class IndexView(TemplateView):
    template_name = 'frontend/index.html'


class ParticipateListView(TemplateView):
    template_name = 'frontend/participate_list.html'

    def get_context_data(self, **kwargs):
        participate_list = Participate.objects.select_related('research').filter(participant=self.request.user)
        context = super(ParticipateListView, self).get_context_data(**kwargs)
        context['participate_list'] = participate_list
        return context


class ParticipateView(View):
    def get(self, request, research_hex):
        research = get_object_or_404(Research, hex=research_hex)
        _participate = Participate.objects.filter(Q(participant=self.request.user) & Q(research=research))
        if _participate.exists():
            participate = _participate[0]
            participate_game_list = ParticipateGameList.objects.order_by('game__order').filter(participate=participate)
            if participate_game_list.filter(is_finish=True).exists():
                is_continue = True
            else:
                is_continue = False
            start_game_id = participate_game_list.exclude(is_finish=True).first().id
            return HttpResponseRedirect(reverse('participate:game', kwargs={'research_hex': research_hex, 'game_id': start_game_id}))
        else:
            # participate = Participate.objects.create(participant=self.request.user, research=research)
            return render(request, 'frontend/agree.html', context={'research': research})

    def post(self, request, research_hex):
        research = get_object_or_404(Research, hex=research_hex)
        form = NameDateForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            participate = Participate.objects.create(participant=self.request.user, research=research)
            participate.agree = True
            participate.agree_name = data['name']
            participate.agree_name = data['date']
            participate.save()
            return HttpResponseRedirect(reverse('participate:research', kwargs={'research_hex': research_hex}))
        else:
            print(form.errors)
            return HttpResponseRedirect(reverse('participate:research', kwargs={'research_hex': research_hex}))


class ParticipateGameView(View):
    def get(self, request, research_hex, game_id):
        research = get_object_or_404(Research, hex=research_hex)
        game = get_object_or_404(Game, Q(research=research) & Q(id=game_id))
        return render(request, 'frontend/game.html', context={'research': research, 'game': game})
