from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('calendar/', views.calendar, name='calendar'),
    path('analytics/', views.analytics, name='analytics'),
    path('heap/', views.heap_visualization, name='heap_visualization'),

    path('api/tasks/', views.api_tasks_dispatch, name='api_tasks'),
    path('api/tasks/<str:task_id>/', views.api_update_task, name='api_update_task'),
    path('api/tasks/<str:task_id>/complete/', views.api_complete_task, name='api_complete_task'),
    path('api/tasks/<str:task_id>/skip/', views.api_skip_task, name='api_skip_task'),
    path('api/tasks/<str:task_id>/delete/', views.api_delete_task, name='api_delete_task'),
    path('api/strategy/', views.api_set_strategy, name='api_set_strategy'),
    path('api/demo/', views.api_run_demo, name='api_run_demo'),
    path('api/undo/', views.api_undo, name='api_undo'),
    path('api/redo/', views.api_redo, name='api_redo'),
]
