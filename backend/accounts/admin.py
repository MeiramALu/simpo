from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import AdminUserCreationForm, UserChangeForm

from .models import User


class UserCreateForm(AdminUserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'full_name')


class UserEditForm(UserChangeForm):
    class Meta:
        model = User
        fields = '__all__'
        field_classes = {}


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_form = UserCreateForm
    form = UserEditForm
    ordering = ['-date_joined']
    list_display = ['email', 'full_name', 'organization', 'country', 'lang', 'email_verified', 'is_staff', 'roles', 'date_joined']
    list_filter = ['email_verified', 'is_staff', 'is_active', 'groups', 'lang', 'country']
    search_fields = ['email', 'full_name', 'organization', 'phone']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Профиль', {'fields': ('full_name', 'organization', 'country', 'phone', 'lang', 'email_verified')}),
        ('Доступ в админку и роль', {
            'fields': ('is_active', 'is_staff', 'groups', 'is_superuser', 'user_permissions'),
            'description': 'Чтобы дать сотруднику доступ: отметьте «Статус персонала» и выберите роль в «Группах»: '
                           'Оргкомитет, Редакция или Администратор симпозиума.',
        }),
        ('Даты', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('email', 'full_name', 'usable_password', 'password1', 'password2')}),
    )

    @admin.display(description='Роли')
    def roles(self, obj):
        return ', '.join(g.name for g in obj.groups.all()) or ('суперпользователь' if obj.is_superuser else '—')

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('groups')

    # --- защита от повышения прав: не-суперпользователь не может
    #     сделать кого-то суперпользователем, выдать права напрямую или править суперпользователя
    def get_readonly_fields(self, request, obj=None):
        ro = list(super().get_readonly_fields(request, obj))
        if not request.user.is_superuser:
            ro += ['is_superuser', 'user_permissions']
        return ro

    def has_change_permission(self, request, obj=None):
        if obj is not None and obj.is_superuser and not request.user.is_superuser:
            return False
        return super().has_change_permission(request, obj)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'groups' and not request.user.is_superuser:
            from django.contrib.auth.models import Group
            from siteconfig.roles import ROLES
            kwargs['queryset'] = Group.objects.filter(name__in=ROLES.keys())
        return super().formfield_for_manytomany(db_field, request, **kwargs)
