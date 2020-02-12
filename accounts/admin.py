from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import ugettext_lazy as _
# Register your account models here.
from .models import User, UserBalance, UserAddress


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Define admin model for custom User model with no email field."""

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('full_name',)}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'is_agent', 'groups', 'user_permissions', )}),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'full_name', 'is_agent', 'is_staff')
    search_fields = ('email', 'full_name')
    exclude = ('paystack_authorization_code',)
    ordering = ('email',)


@admin.register(UserAddress)
class AddressAdmin(admin.ModelAdmin):

    search_fields = ['user']
    list_display = ['user', 'street_address']


admin.site.register(UserBalance)
