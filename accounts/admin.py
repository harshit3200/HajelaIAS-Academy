from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Department, FeaturePermission


# ---------------- FeaturePermission Inline ----------------
class FeaturePermissionInline(admin.TabularInline):
    model = FeaturePermission
    extra = 1
    verbose_name = "Feature Permission"
    verbose_name_plural = "Feature Permissions"


# ---------------- Custom UserAdmin ----------------
class UserAdmin(BaseUserAdmin):
    list_display = (
        'email', 'user_type', 'is_staff', 'is_superuser', 'is_active',
        'is_verified', 'is_approved', 'department',
        'staff_approval_rights', 'admin_approval_rights'
    )
    list_filter = (
        'user_type', 'is_staff', 'is_superuser',
        'department', 'is_verified', 'is_approved'
    )

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions'
            )
        }),
        (_('Approval Rights'), {
            'fields': (
                'staff_approval_rights',
                'admin_approval_rights',
                'is_verified',
                'is_approved'
            )
        }),
        (_('Organizational Info'), {'fields': ('department', 'user_type')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'password1', 'password2',
                'user_type', 'department'
            ),
        }),
    )

    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)

    actions = ['approve_users']

    inlines = [FeaturePermissionInline]  # ✅ Inline feature permissions

    @admin.action(description="✅ Approve selected users")
    def approve_users(self, request, queryset):
        queryset.update(is_approved=True)


# ---------------- DepartmentAdmin ----------------
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'head', 'created_at')
    search_fields = ('name',)
    list_filter = ('name',)
    ordering = ('name',)


# ---------------- Register Models ----------------
admin.site.register(User, UserAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(FeaturePermission)
