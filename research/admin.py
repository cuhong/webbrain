import datetime

import pytz
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django_summernote.admin import SummernoteModelAdmin
from import_export import resources
from import_export.admin import ExportMixin
from ordered_model.admin import OrderedTabularInline, OrderedModelAdmin, OrderedInlineModelAdminMixin
from ordered_model.models import OrderedModel
from django_json_widget.widgets import JSONEditorWidget

from research.forms import ResearchAdminAuthenticationForm
from research.models import ResearchAdminProxyForResearch, Game, Research, Agree, ParticipateAdminProxy, \
    ParticipateGameListAdminProxy, Poll
from participate.models import Participate


class ResearchAdmin(admin.AdminSite):
    site_header = 'webbrain 연구자 사이트'
    site_title = site_header
    index_title = site_header

    login_form = ResearchAdminAuthenticationForm

    def has_permission(self, request):
        try:
            return request.user.is_researcher
        except:
            return False
    # TODO redirect to 오류 페이지


research_site = ResearchAdmin(name='research_admin_site')


class GameInlineAdmin(OrderedTabularInline):
    verbose_name = '게임'
    verbose_name_plural = verbose_name
    model = Game
    fields = ('game_title', 'game_file', 'order', 'parse_result', 'move_up_down_links')
    readonly_fields = ('order', 'parse_result', 'move_up_down_links')
    ordering = ('order',)


class AgreeInlineAdmin(admin.StackedInline):
    model = Agree
    fields = ('item',)
    extra = 3


class ResearchPollInlineAdmin(OrderedTabularInline):
    verbose_name = '설문'
    verbose_name_plural = verbose_name
    model = Poll
    fields = ('question', 'question_type', 'choices', 'required', 'move_up_down_links')
    readonly_fields = ('move_up_down_links',)


@admin.register(ResearchAdminProxyForResearch, site=research_site)
class ResearchModelAdmin(OrderedInlineModelAdminMixin, SummernoteModelAdmin, admin.ModelAdmin):
    # 연구자용 연구 페이지
    list_display = ('project_title', 'user', 'status', 'link')
    readonly_fields = ('status', 'user',)
    summernote_fields = ('project_agreement',)

    inlines = (GameInlineAdmin, AgreeInlineAdmin, ResearchPollInlineAdmin)

    def link(self, obj):
        url = reverse('participate:research', kwargs={'research_hex': obj.hex})
        full_url = ''.join(['http://', get_current_site(self.request).domain, url])
        return full_url

    link.short_description = '주소'

    def get_queryset(self, request):
        self.request = request
        queryset = super(ResearchModelAdmin, self).get_queryset(request)
        return queryset.filter(user=request.user)

    def get_fieldsets(self, request, obj=None):
        if obj:
            fieldsets = (
                ('기본정보', {'fields': (
                    'project_title', 'project_description', 'project_agreement', 'project_start_date', 'tags',
                    'status',)}),
            )
        else:
            fieldsets = (
                ('기본정보', {'fields': (
                    'project_title', 'project_description', 'project_agreement', 'project_start_date', 'tags')}),
            )
        fieldsets += (
            ('리워드', {'fields': ('reward', 'reward_description')}),
        )
        return fieldsets

    def save_model(self, request, obj, form, change):
        if not change:
            obj.user = request.user
        super(ResearchModelAdmin, self).save_model(request, obj, form, change)


class ParticipateGameListInlineAdmin(admin.TabularInline):
    model = ParticipateGameListAdminProxy
    readonly_fields = ['game', 'finished_dt', 'response_time', 'score']
    fields = ['game', 'finished_dt', 'response_time', 'score']
    extra = 0

    def response_time(self, obj):
        result = obj.calculate_score()
        return "{}초".format(round(result['avg_rt'], 2))

    response_time.short_description = '평균응답시간'

    def score(self, obj):
        result = obj.calculate_score()
        try:
            score = result['score']['correct'] / result['score']['count']
        except:
            score = 0
        return "{}%".format(round(score * 100, 2))

    score.short_description = '정답률'

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False


class ParticipateResource(resources.ModelResource):
    class Meta:
        model = ParticipateAdminProxy
        fields = ['research', 'participate_at', 'participant', 'agree_name', 'agree', 'poll']
        export_order = ['research', 'participate_at', 'participant', 'agree_name', 'agree', 'poll']

    research = resources.Field(attribute='research', column_name='연구')
    participate_at = resources.Field(attribute='participate_at', column_name='연구참여일시')
    participant = resources.Field(attribute='participant', column_name='피험자(아이디)')
    agree_name = resources.Field(attribute='agree_name', column_name='동의자명')
    agree = resources.Field(attribute='agree', column_name='동의여부')
    poll = resources.Field(attribute='poll', column_name='설문')

    def dehydrate_research(self, obj):
        return obj.research.project_title

    def dehydrate_participate_at(self, obj):
        local_tz = pytz.timezone('Asia/Seoul')
        return obj.participate_at.replace(tzinfo=pytz.utc).astimezone(local_tz)

    def dehydrate_participant(self, obj):
        return obj.participant.__str__()

    def dehydrate_agree(self, obj):
        if obj.agree:
            return '동의'
        else:
            return '미동의'


@admin.register(ParticipateAdminProxy, site=research_site)
class ParticipateAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = ParticipateResource
    readonly_fields = ['participate_at', 'participant', 'research', 'agree', 'agree_name', ]
    list_filter = ['research', 'participant', 'agree']
    list_display = ['research', 'participate_at', 'participant', 'agree_name', 'agree']
    inlines = [ParticipateGameListInlineAdmin]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        queryset = super(ParticipateAdmin, self).get_queryset(request)
        return queryset.filter(research__user=request.user)


class ResearchFilter(SimpleListFilter):
    title = '연구'
    parameter_name = 'research'

    def lookups(self, request, model_admin):
        research_list = Research.objects.values_list('id', 'project_title').filter(user=request.user)
        return research_list

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(id=self.value())
        else:
            return queryset


class ParticipateGameListResource(resources.ModelResource):
    class Meta:
        model = ParticipateGameListAdminProxy
        fields = ['research', 'participant', 'game', 'finished_dt', 'response_time', 'score', 'result']
        export_order = ['research', 'participant', 'game', 'finished_dt', 'response_time', 'score', 'result']

    research = resources.Field(column_name='연구')
    participant = resources.Field(column_name='피험자(아이디)')
    game = resources.Field(column_name='game')
    finished_dt = resources.Field(attribute='finished_dt', column_name='참여일시')
    response_time = resources.Field(column_name='평균응답시간(초)')
    score = resources.Field(column_name='정답률')
    result = resources.Field(attribute='result', column_name='응답원본')

    def dehydrate_research(self, obj):
        return obj.participate.research.project_title

    def dehydrate_participant(self, obj):
        return obj.participate.participant.__str__()

    def dehydrate_game(self, obj):
        return obj.game.game_title

    def dehydrate_finished_dt(self, obj):
        local_tz = pytz.timezone('Asia/Seoul')
        return obj.finished_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)

    def dehydrate_response_time(self, obj):
        result = obj.calculate_score()
        return round(result['avg_rt'], 2)

    def dehydrate_score(self, obj):
        result = obj.calculate_score()
        try:
            score = result['score']['correct'] / result['score']['count']
        except:
            score = 0
        return round(score * 100, 2)


class ParticipateGameListResearchFilter(SimpleListFilter):
    title = '연구'
    parameter_name = 'research'

    def lookups(self, request, model_admin):
        research_list = Research.objects.values_list('id', 'project_title').filter(user=request.user)
        return research_list

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(participate__research_id=self.value())
        else:
            return queryset


class ParticipateGameListGameFilter(SimpleListFilter):
    title = '게임'
    parameter_name = 'game'

    def lookups(self, request, model_admin):
        game_list = Game.objects.values_list('id', 'game_title').filter(research__user=request.user)
        return game_list

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(game_id=self.value())
        else:
            return queryset


@admin.register(ParticipateGameListAdminProxy, site=research_site)
class ParticipateGameListAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ['research', 'participant', 'game', 'finished_dt', 'response_time', 'score']
    list_filter = [ParticipateGameListResearchFilter, ParticipateGameListGameFilter]
    resource_class = ParticipateGameListResource

    def get_queryset(self, request):
        queryset = super(ParticipateGameListAdmin, self).get_queryset(request)
        return queryset.filter(participate__research__user=request.user)

    def research(self, obj):
        return obj.participate.research

    research.short_description = '연구'

    def participant(self, obj):
        return obj.participate.participant

    participant.short_description = '참여자'

    def response_time(self, obj):
        result = obj.calculate_score()
        return "{}초".format(round(result['avg_rt'], 2))

    response_time.short_description = '평균응답시간'

    def score(self, obj):
        result = obj.calculate_score()
        try:
            score = result['score']['correct'] / result['score']['count']
        except:
            score = 0
        return "{}%".format(round(score * 100, 2))

    score.short_description = '정답률'

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
