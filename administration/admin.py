from django.contrib import admin
from django.contrib.auth.forms import UserChangeForm
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import Q
from django.urls import reverse
from django_summernote.admin import SummernoteModelAdmin

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
        return queryset.filter(is_researcher=True)


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
        return queryset.exclude(Q(is_staff=True) | Q(is_researcher=True))  # TODO 필터 변경


@admin.register(ResearchAdminProxy, site=admin_site)
class ResearchModelAdmin(SummernoteModelAdmin, admin.ModelAdmin):
    list_display = ('project_title', 'user', 'status', 'link')
    list_filter = ('status',)
    readonly_fields = ('user',)
    summernote_fields = ('project_agreement',)
    fieldsets = (
        ('기본정보', {'fields': (
            'project_title', 'project_description', 'user', 'project_agreement', 'project_start_date', 'tags',
            'status', )}),
        ('참여조건', {'fields': ('condition_age_min', 'condition_age_max', 'condition_gender')}),
        ('리워드', {'fields': ('reward', 'reward_description',)}),
    )

    def link(self, obj):
        url = reverse('participate:research', kwargs={'research_hex': obj.hex})
        full_url = ''.join(['http://', get_current_site(self.request).domain, url])
        return full_url

    link.short_description = '연구참여주소'

    # readonly_fields = [field.name for field in ResearchAdminProxy._meta.fields if
    #                    field.name not in ['is_block']] + ['tags']

    def has_add_permission(self, request):
        return False

    def get_queryset(self, request):
        self.request = request
        queryset = super(ResearchModelAdmin, self).get_queryset(request)
        return queryset
