from django.contrib import admin
from django.utils import timezone
from .models import App, Feature, Operation, RegistrationRequest, PermissionRequest

class AuditableModelAdmin(admin.ModelAdmin):
    """
    Base admin class for auditable models.
    """
    readonly_fields = ('created_by', 'created_at', 'updated_by', 'updated_at')
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(App)
class AppAdmin(AuditableModelAdmin):
    list_display = ('name', 'description', 'is_active', 'created_by', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')

@admin.register(Feature)
class FeatureAdmin(AuditableModelAdmin):
    list_display = ('name', 'app', 'description', 'is_active', 'created_by', 'created_at')
    list_filter = ('app', 'is_active', 'created_at')
    search_fields = ('name', 'description', 'app__name')
    autocomplete_fields = ['app']

@admin.register(Operation)
class OperationAdmin(AuditableModelAdmin):
    list_display = ('name', 'feature', 'description', 'is_active', 'created_by', 'created_at')
    list_filter = ('feature__app', 'feature', 'is_active', 'created_at')
    search_fields = ('name', 'description', 'feature__name', 'feature__app__name')
    autocomplete_fields = ['feature']

@admin.register(RegistrationRequest)
class RegistrationRequestAdmin(AuditableModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'organization', 'status', 'created_at')
    list_filter = ('status', 'created_at', 'processed_at')
    search_fields = ('email', 'first_name', 'last_name', 'organization')
    readonly_fields = AuditableModelAdmin.readonly_fields + ('processed_at', 'processed_by')
    
    def save_model(self, request, obj, form, change):
        if 'status' in form.changed_data:
            obj.processed_at = timezone.now()
            obj.processed_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(PermissionRequest)
class PermissionRequestAdmin(AuditableModelAdmin):
    list_display = ('requesting_user', 'app', 'feature', 'operation', 'status', 'created_at')
    list_filter = ('status', 'app', 'feature', 'created_at', 'processed_at')
    search_fields = (
        'requesting_user__email',
        'app__name',
        'feature__name',
        'operation__name'
    )
    readonly_fields = AuditableModelAdmin.readonly_fields + ('processed_at', 'processed_by')
    autocomplete_fields = ['app', 'feature', 'operation', 'requesting_user']

    def save_model(self, request, obj, form, change):
        if 'status' in form.changed_data:
            obj.processed_at = timezone.now()
            obj.processed_by = request.user
        super().save_model(request, obj, form, change)

# Customize admin site header and title
admin.site.site_header = 'User Management Administration'
admin.site.site_title = 'User Management Admin Portal'
admin.site.index_title = 'Welcome to User Management Portal'
