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
from research.models import Research, Game

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

        if _participate.agree:
            participated_game_list = ParticipateGameList.objects.select_related('game').filter(Q(participate=_participate)).distinct('game_id')
            unparticipated_game_list = research.game_set.filter(Q(parse_result=True) & ~Q(id__in=[p.game.id for p in participated_game_list]))

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


class ParticipantSignupView(View):
    def get(self, request):
        form = CustomParticipantUserCreationForm()
        return render(request, 'frontend/auth/signup.html', context={'form': form})

    def post(self, request):
        form = CustomParticipantUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('participate:index')
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
        participate = get_object_or_404(Participate, Q(participant=self.request.user) & Q(research=research) & Q(agree=True))
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
            ParticipateGameList.objects.create(participate=participate, game=game, result=data)
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
        ParticipateGameList.objects.create(participate=participate, game=game, result=data)
        context = {'result': True, 'message': '게임 결과가 전송되었습니다.'}
        return HttpResponse(json.dumps(context), content_type='application/json')


class GameResultView(LoginRequiredMixin, View):
    def get(self, request, research_hex, game_id):
        research = get_object_or_404(Research, Q(hex=research_hex))
        participate = get_object_or_404(Participate, Q(participant=self.request.user) & Q(research=research) & Q(agree=True))
        game = get_object_or_404(Game, Q(research=research) & Q(id=game_id))
        result_list = ParticipateGameList.objects.filter(Q(participate=participate) & Q(game=game))
        context = {'result_list': result_list, 'research': research,}
        return render(request, template_name='frontend/game_result.html', context=context)


# class ParticipateLogoutView(LogoutView):

# class ParticipantLoginView(View):
#     def get(self, request):
#         form = CustomLoginView()
#         return render(request, 'frontend/auth/login.html', context={'form': form})
#
#     def post(self, request):
#         form = CustomLoginView(request.POST)
#         if form.is_valid():
#             data = form.cleaned_data
#             user = authenticate(request, email=data['user'], password=data['password'])
#             if user:
#                 login(request, user)
#                 return HttpResponseRedirect(reverse('participate:index'))
#             else:
#                 return HttpResponse('로그인 실패')
#         else:
#             return render(request, 'frontend/auth/login.html', context={'form': form})
