from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Main views (require login)
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('calendar/', views.calendar, name='calendar'),
    path('analytics/', views.analytics, name='analytics'),
    
    # API endpoints (require login)
    path('api/tasks/', views.api_add_task, name='api_add_task'),
    path('api/tasks/<str:task_id>/', views.api_update_task, name='api_update_task'),
    path('api/tasks/<str:task_id>/complete/', views.api_complete_task, name='api_complete_task'),
    path('api/tasks/<str:task_id>/skip/', views.api_skip_task, name='api_skip_task'),
    path('api/tasks/<str:task_id>/delete/', views.api_delete_task, name='api_delete_task'),
    path('api/tasks/', views.api_get_tasks, name='api_get_tasks'),
    path('api/undo/', views.api_undo, name='api_undo'),
    path('api/redo/', views.api_redo, name='api_redo'),
]

