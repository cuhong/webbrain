import json

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import TemplateView

from participate.forms import ResearchAgreeForm
from participate.models import Participate, ParticipateGameList
from administration.models import MainPage
from research.models import Research, Game, Poll

from research.parsers import Parser
from users.forms import CustomParticipantUserCreationForm
from django.contrib.auth import views as auth_views


class IndexView(TemplateView):
    template_name = 'frontend/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page'] = MainPage.get_solo()
        return context


class ParticipateListView(LoginRequiredMixin, TemplateView):
    template_name = 'frontend/participate_list.html'
    login_url = reverse_lazy('participate:login')

    def get_context_data(self, **kwargs):
        participate_list = Participate.objects.select_related('research').filter(participant=self.request.user)
        context = super(ParticipateListView, self).get_context_data(**kwargs)
        context['participate_list'] = participate_list
        return context


class ResearchView(LoginRequiredMixin, View):
    login_url = reverse_lazy('participate:login')

    def get(self, request, research_hex):
        research = get_object_or_404(Research.objects.prefetch_related('game_set'), hex=research_hex)
        _participate, created = Participate.objects.get_or_create(participant=self.request.user, research=research)
        poll_list = Poll.objects.filter(research=research)
        if _participate.agree:
            if poll_list.exists() and _participate.poll is None:
                context = {'research': research, 'poll_list': poll_list}
                return render(request, 'frontend/poll.html', context=context)

            participated_game_list = ParticipateGameList.objects.select_related('game').filter(
                Q(participate=_participate)).distinct('game_id')
            unparticipated_game_list = research.game_set.filter(
                Q(parse_result=True) & ~Q(id__in=[p.game.id for p in participated_game_list]))

            return render(request, 'frontend/game_list.html', context={'research': research,
                                                                       'participated_game_list': participated_game_list,
                                                                       'unparticipated_game_list': unparticipated_game_list})
        else:
            form = ResearchAgreeForm(instance=_participate)
            return render(request, 'frontend/agree.html', context={'research': research, 'form': form})

    def post(self, request, research_hex):
        research = get_object_or_404(Research, hex=research_hex)
        participate = get_object_or_404(Participate, Q(participant=self.request.user) & Q(research=research))
        form = ResearchAgreeForm(request.POST, instance=participate)
        if form.is_valid():
            data = form.cleaned_data
            _participate = form.save(commit=False)
            _participate.agree = True
            _participate.save()
            return HttpResponseRedirect(reverse('participate:research', kwargs={'research_hex': research_hex}))
        else:
            print(form.errors)
            return HttpResponseRedirect(reverse('participate:research', kwargs={'research_hex': research_hex}))


class ResearchPollView(LoginRequiredMixin, View):

    def post(self, request, research_hex):
        research = get_object_or_404(Research.objects.prefetch_related('game_set'), hex=research_hex)
        _participate, created = Participate.objects.get_or_create(participant=self.request.user, research=research)
        poll_list = Poll.objects.filter(research=research)
        if poll_list.exists():
            if _participate.poll is None:
                data = request.POST
                try:
                    poll_result = {}
                    for k, v in data.items():
                        if 'poll' in k:
                            poll_id = int(k.split('_')[-1])
                            poll = Poll.objects.get(id=poll_id)
                            question = poll.question
                            poll_value = str(v) if poll.question_type == 0 else poll.select()[int(v[0])-1]['value']
                            poll_json = json.loads(json.dumps(poll_value))
                            poll_result.update({question: poll_json})
                    print(poll_result)
                except:
                    context = {'message': '저장 실패'}
                else:
                    _participate.poll = poll_result
                    _participate.save()
                    context = {'message': '저장 성공'}
                return HttpResponse(json.dumps(context), content_type='application/json')
            else:
                context = {'message': '이미 참여한 설문입니다.'}
                return HttpResponse(json.dumps(context), content_type='application/json')
        else:
            context = {'message': '잘못된 접근.'}
            return HttpResponse(json.dumps(context), content_type='application/json')


class ParticipantSignupView(View):
    def get(self, request):
        form = CustomParticipantUserCreationForm()
        next = request.GET.get('next', None)
        return render(request, 'frontend/auth/signup.html', context={'form': form, 'next': next})

    def post(self, request):
        form = CustomParticipantUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            next = form.cleaned_data.get('next', reverse_lazy('participate:index'))
            return HttpResponseRedirect(next)
        else:
            return render(request, 'frontend/auth/signup.html', context={'form': form})


class ParticipantLoginView(LoginView):
    template_name = 'frontend/auth/login.html'
    redirect_field_name = 'next'
    redirect_authenticated_user = True


class ParticipantLogoutView(LoginRequiredMixin, View):
    login_url = reverse_lazy('participate:login')

    def get(self, request):
        auth_views.auth_logout(request)
        return HttpResponseRedirect(reverse_lazy('participate:login'))


class GameView(LoginRequiredMixin, View):
    def get(self, request, research_hex, game_id):
        research = get_object_or_404(Research, hex=research_hex)
        participate = get_object_or_404(Participate,
                                        Q(participant=self.request.user) & Q(research=research) & Q(agree=True))
        game = get_object_or_404(Game, Q(research=research) & Q(id=game_id))
        if ParticipateGameList.objects.filter(Q(participate=participate) & Q(game=game)).exists():
            messages.info(request, '이미 참여한 게임입니다.')
            return HttpResponseRedirect(reverse_lazy('participate:research', kwargs={"research_hex": research_hex}))
        data = game.game_json
        media_url = game._game_media_url
        context = {'data': data, 'media_url': media_url, 'game': game, 'research_hex': research_hex}
        return render(request, template_name='game/game.html', context=context)

    def post(self, request, research_hex, game_id):
        research = get_object_or_404(Research, hex=research_hex)
        game = get_object_or_404(Game, Q(research=research) & Q(id=game_id))
        participate = get_object_or_404(Participate, Q(participant=self.request.user) & Q(research=research))
        if ParticipateGameList.objects.filter(Q(participate=participate) & Q(game=game)).exists():
            context = {'result': False, 'message': '이미 참여한 게임입니다.'}
        else:
            json_data = request.POST.get('json_result')
            data = json.loads(json_data)
            pgl = ParticipateGameList.objects.create(participate=participate, game=game, result=data)
            pgl.calculate_score()
            context = {'result': True, 'message': '게임 결과가 전송되었습니다.'}
        return HttpResponse(json.dumps(context), content_type='application/json')


class GameRetestView(LoginRequiredMixin, View):
    def get(self, request, research_hex, game_id):
        research = get_object_or_404(Research, hex=research_hex)
        game = get_object_or_404(Game, Q(research=research) & Q(id=game_id))
        data = game.game_json
        media_url = game._game_media_url
        context = {'data': data, 'media_url': media_url, 'game': game, 'research_hex': research_hex}
        return render(request, template_name='game/game.html', context=context)

    def post(self, request, research_hex, game_id):
        research = get_object_or_404(Research, hex=research_hex)
        game = get_object_or_404(Game, Q(research=research) & Q(id=game_id))
        participate = get_object_or_404(Participate, Q(participant=self.request.user) & Q(research=research))
        json_data = request.POST.get('json_result')
        data = json.loads(json_data)
        pgl = ParticipateGameList.objects.create(participate=participate, game=game, result=data)
        pgl.calculate_score()
        context = {'result': True, 'message': '게임 결과가 전송되었습니다.'}
        return HttpResponse(json.dumps(context), content_type='application/json')


def rank(value_list, value, reverse=False):
    _find = [True if v == value else False for v in value_list]
    if _find.count(True) == 0:
        return 0
    for idx, _value in enumerate(sorted(value_list, reverse=reverse)):
        if _value == value:
            return idx + 1


class GameResultView(LoginRequiredMixin, View):
    def get(self, request, research_hex, game_id):
        research = get_object_or_404(Research, Q(hex=research_hex))
        participate = get_object_or_404(Participate,
                                        Q(participant=self.request.user) & Q(research=research) & Q(agree=True))
        game = get_object_or_404(Game, Q(research=research) & Q(id=game_id))
        result_list = ParticipateGameList.objects.values().filter(Q(participate=participate) & Q(game=game))
        game_result_list = ParticipateGameList.objects.values('count', 'correct', 'response_time').filter(game=game)
        response_time_list = [result['response_time'] for result in game_result_list]
        correct_list = [result['correct'] for result in game_result_list]
        for game_result in result_list:
            game_result.update({'rank': {}})
            game_result['rank']['correct'] = rank(correct_list, game_result['correct'], reverse=True)
            game_result['rank']['response_time'] = rank(response_time_list, game_result['response_time'])
        context = {'result_list': result_list, 'research': research, 'response_time_list': response_time_list,
                   'correct_list': correct_list}
        return render(request, template_name='frontend/game_result.html', context=context)
