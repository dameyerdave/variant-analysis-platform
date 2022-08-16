from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.forms import CustomUserCreationForm, CustomUserChangeForm
from users.models import User


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = ('email', 'first_name', 'last_name',
                    'is_staff', 'is_active', 'get_groups')
    list_filter = ('is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('email', 'password', 'first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
        ('Groups', {'fields': ('groups',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'is_staff', 'is_active')}
         ),
    )
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email', 'first_name', 'last_name')

    def get_groups(self, obj):
        return ', '.join([group.name for group in obj.groups.all()])
    get_groups.short_description = 'Groups'

    def save_form(self, request, form, change):
        # Needs to be overwritten to call create_user
        if not change:
            form.instance = self.model.objects.create_user(
                form.cleaned_data['email'],
                form.cleaned_data['password1'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name']
            )
        return super().save_form(request, form, change)


admin.site.register(User, CustomUserAdmin)
