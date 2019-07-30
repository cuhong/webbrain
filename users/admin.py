from django.contrib import admin
from django.contrib.auth.admin import UserAdmin


class BaseUserAdmin(UserAdmin, ):
    filter_horizontal = ()
    ordering = ('date_joined',)
    search_fields = ('email', 'name')
    fieldsets = (
        (None, {'fields': ('email', 'name', 'password', 'date_joined', 'is_researcher', 'is_researcher')}),
    )

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = ('date_joined',)
        if obj:
            readonly_fields += ('email', 'name', 'is_researcher_accepted_at')
        return readonly_fields
