from django.contrib import admin
from .models import TaskModel

@admin.register(TaskModel)
class TaskModelAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'project', 'domain', 'status', 'priority_score', 'deadline', 'created_at']
    list_filter = ['status', 'project', 'domain', 'user', 'created_at']
    search_fields = ['title', 'project', 'domain', 'user__username', 'user__email']
    ordering = ['-created_at', 'priority_score']
    readonly_fields = ['id', 'created_at', 'priority_score']
    list_editable = ['status']  # Allow quick status changes
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'user', 'title', 'project', 'domain')
        }),
        ('Task Details', {
            'fields': ('deadline', 'difficulty', 'estimated_effort', 'importance', 'status')
        }),
        ('Priority & Dates', {
            'fields': ('priority_score', 'created_at', 'completed_at')
        }),
    )
    
    def get_queryset(self, request):
        """Superusers can see all tasks, regular users see only their own"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

