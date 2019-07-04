from django.contrib import admin
from django.contrib.auth.forms import UserChangeForm

from research.models import ResearchAdminProxy
from users.admin import BaseUserAdmin
from users.forms import CustomParticipantUserCreationForm, CustomStaffUserCreationForm, CustomResearcherUserCreationForm
from users.models import StaffUser, ResearcherUser, ParticipantUser


class AdminisitrationAdmin(admin.AdminSite):
    site_header = 'webbrain 관리자 사이트'
    site_title = site_header
    index_title = site_header


admin_site = AdminisitrationAdmin(name='administration_admin')


@admin.register(StaffUser, site=admin_site)
class StaffUserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = CustomStaffUserCreationForm
    exclude = ('username',)
    list_display = ('email', 'name', 'date_joined',)
    list_filter = ()
    add_fieldsets = ((None, {'fields': ('email', 'name', 'password1', 'password2', 'is_superuser')}),)
    fieldsets = (
        ('기본정보', {'fields': ('email', 'name', 'is_active', 'date_joined')}),
        ('권한정보', {'fields': ('is_staff',)})
    )

    def get_queryset(self, request):
        queryset = super(StaffUserAdmin, self).get_queryset(request)
        return queryset.filter(is_staff=True)


@admin.register(ResearcherUser, site=admin_site)
class ResearcherUserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = CustomResearcherUserCreationForm
    list_display = ('email', 'name', 'date_joined',)
    list_filter = ()
    exclude = ('username',)
    add_fieldsets = ((None, {'fields': ('email', 'name', 'password1', 'password2')}),)
    fieldsets = (
        ('기본정보', {'fields': ('email', 'name', 'is_active', 'date_joined')}),
        ('권한정보', {'fields': ('is_researcher', 'is_researcher_accepted_at', 'groups', 'user_permissions')})
    )

    def get_queryset(self, request):
        queryset = super(ResearcherUserAdmin, self).get_queryset(request)
        return queryset.filter(is_researcher__in=[True, False])


@admin.register(ParticipantUser, site=admin_site)
class ParticipantUserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = CustomParticipantUserCreationForm
    list_display = ('email', 'name', 'date_joined',)
    list_filter = ()
    exclude = ('username',)
    add_fieldsets = ((None, {'fields': ('email', 'name', 'password1', 'password2')}),)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super(ParticipantUserAdmin, self).get_readonly_fields(request, obj)
        return readonly_fields

    def get_queryset(self, request):
        queryset = super(ParticipantUserAdmin, self).get_queryset(request)
        return queryset.exclude(is_staff__in=[True, False])  # TODO 필터 변경


@admin.register(ResearchAdminProxy, site=admin_site)
class ResearchModelAdmin(admin.ModelAdmin):
    list_display = ('project_title', 'user', 'is_open', 'status')
    list_filter = ('status',)
    fieldsets = (
        ('기본정보', {'fields': (
            'project_title', 'project_description', 'user', 'project_agreement', 'project_start_date',
            'project_end_date', 'tags',
            'status', )}),
        ('동의조건', {'fields': ('agree_name', 'agree_tel', 'agree_gender', 'agree_email', 'agree_age')}),
        ('참여조건', {'fields': ('condition_age_min', 'condition_age_max', 'condition_gender')}),
        ('리워드', {'fields': ('reward', 'reward_description',)}),
    )

    # readonly_fields = [field.name for field in ResearchAdminProxy._meta.fields if
    #                    field.name not in ['is_block']] + ['tags']

    def has_add_permission(self, request):
        return False
