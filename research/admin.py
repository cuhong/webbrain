from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from ordered_model.admin import OrderedTabularInline, OrderedModelAdmin
from ordered_model.models import OrderedModel

from research.forms import ResearchAdminAuthenticationForm
from research.models import ResearchAdminProxyForResearch, Game, Research, Agree


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
    fields = ('game_title', 'game_file', 'order', 'move_up_down_links')
    readonly_fields = ('order', 'move_up_down_links')
    ordering = ('order',)


class AgreeInlineAdmin(admin.StackedInline):
    model = Agree
    fields = ('item',)
    extra = 3


@admin.register(ResearchAdminProxyForResearch, site=research_site)
class ResearchModelAdmin(SummernoteModelAdmin, OrderedModelAdmin):

    # 연구자용 연구 페이지
    list_display = ('project_title', 'user', 'status')
    readonly_fields = ('status', 'user',)
    summernote_fields = ('project_agreement',)

    inlines = (GameInlineAdmin, AgreeInlineAdmin)

    def get_queryset(self, request):
        queryset = super(ResearchModelAdmin, self).get_queryset(request)
        return queryset.filter(user=request.user)

    def get_fieldsets(self, request, obj=None):
        if obj:
            fieldsets = (
                ('기본정보', {'fields': (
                    'project_title', 'project_description', 'project_agreement', 'project_start_date', 'tags', 'status',)}),
            )
        else:
            fieldsets = (
                ('기본정보', {'fields': (
                    'project_title', 'project_description', 'project_agreement', 'project_start_date', 'tags')}),
            )
        fieldsets += (
            ('동의조건', {'fields': ('agree_name', 'agree_tel', 'agree_gender', 'agree_email', 'agree_age')}),
            ('참여조건', {'fields': ('condition_age_min', 'condition_age_max', 'condition_gender')}),
            ('리워드', {'fields': ('reward', 'reward_description')}),
        )
        return fieldsets

    def save_model(self, request, obj, form, change):
        if not change:
            obj.user = request.user
        super(ResearchModelAdmin, self).save_model(request, obj, form, change)
