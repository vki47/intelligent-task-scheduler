import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.contrib import messages
from datetime import datetime
from .core_classes import Scheduler, Task, WorkSession, UndoRedoManager, TaskHistory
from .models import TaskModel

# User-specific instances stored in a dictionary
user_schedulers = {}
user_undo_redo = {}
user_history = {}

# Get or create user-specific scheduler
def get_user_scheduler(user):
    """Get or create scheduler for a specific user"""
    if user.id not in user_schedulers:
        user_schedulers[user.id] = Scheduler()
        load_tasks_from_db(user)
    return user_schedulers[user.id]

def get_user_undo_redo(user):
    """Get or create undo/redo manager for a specific user"""
    if user.id not in user_undo_redo:
        user_undo_redo[user.id] = UndoRedoManager()
    return user_undo_redo[user.id]

def get_user_history(user):
    """Get or create history for a specific user"""
    if user.id not in user_history:
        user_history[user.id] = TaskHistory()
    return user_history[user.id]

# Load tasks from database for a specific user
def load_tasks_from_db(user):
    """Load tasks from database into scheduler for a specific user"""
    try:
        scheduler = user_schedulers[user.id]
        tasks = TaskModel.objects.filter(user=user)
        for task_model in tasks:
            # Ensure deadline is timezone-aware if it exists
            deadline = task_model.deadline
            if deadline and deadline.tzinfo is None:
                deadline = timezone.make_aware(deadline)
            
            task = Task(
                title=task_model.title,
                project=task_model.project,
                domain=task_model.domain,
                deadline=deadline,
                difficulty=task_model.difficulty,
                estimated_effort=task_model.estimated_effort,
                importance=task_model.importance,
                status=task_model.status,
                task_id=task_model.id,
                created_at=task_model.created_at,
                completed_at=task_model.completed_at
            )
            scheduler.tasks[task.id] = task
            if task.status == 'pending' or task.status == 'in-progress':
                scheduler.priority_queue.enqueue(task)
    except Exception:
        # Database tables don't exist yet, skip loading
        pass


def register_view(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserCreationForm()
    
    # Remove help text from form fields
    form.fields['username'].help_text = ''
    form.fields['password1'].help_text = ''
    form.fields['password2'].help_text = ''
    
    return render(request, 'scheduler/register.html', {'form': form})


def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'scheduler/login.html')


@login_required
def logout_view(request):
    """User logout view"""
    from django.contrib.auth import logout
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


@login_required
def dashboard(request):
    """Dashboard view"""
    scheduler = get_user_scheduler(request.user)
    scheduler.recalculate_priorities()
    tasks = scheduler.get_all_tasks()
    stats = scheduler.get_stats()
    
    context = {
        'tasks': [task.to_dict() for task in tasks],
        'stats': stats,
        'next_task': scheduler.get_next_task().to_dict() if scheduler.get_next_task() else None
    }
    return render(request, 'scheduler/dashboard.html', context)


@login_required
def calendar(request):
    """Calendar view - Monthly grid like Notion"""
    from calendar import monthrange
    import calendar as cal_module
    
    scheduler = get_user_scheduler(request.user)
    scheduler.recalculate_priorities()
    tasks = scheduler.get_all_tasks()
    
    # Get current month/year or from query params
    now = timezone.now()
    year = int(request.GET.get('year', now.year))
    month = int(request.GET.get('month', now.month))
    
    # Get first day of month and number of days
    first_day = datetime(year, month, 1)
    num_days = monthrange(year, month)[1]
    
    # Get the day of week for the first day (0 = Monday, 6 = Sunday)
    first_weekday = first_day.weekday()
    
    # Group tasks by date (day number)
    tasks_by_date = {}
    for task in tasks:
        if task.deadline:
            if isinstance(task.deadline, str):
                deadline = datetime.fromisoformat(task.deadline.replace('Z', '+00:00'))
                if deadline.tzinfo is None:
                    deadline = timezone.make_aware(deadline)
            else:
                deadline = task.deadline
                if deadline.tzinfo is None:
                    deadline = timezone.make_aware(deadline)
            
            # Only include tasks from current month
            if deadline.year == year and deadline.month == month:
                day_num = deadline.day
                if day_num not in tasks_by_date:
                    tasks_by_date[day_num] = []
                tasks_by_date[day_num].append(task.to_dict())
    
    # Create calendar days list with tasks
    calendar_days = []
    for day in range(1, num_days + 1):
        calendar_days.append({
            'day': day,
            'tasks': tasks_by_date.get(day, []),
            'is_today': (day == now.day and now.year == year and now.month == month)
        })
    
    # Calculate previous and next month
    if month == 1:
        prev_month = 12
        prev_year = year - 1
    else:
        prev_month = month - 1
        prev_year = year
    
    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year
    
    context = {
        'year': year,
        'month': month,
        'month_name': cal_module.month_name[month],
        'first_weekday': first_weekday,
        'num_days': num_days,
        'calendar_days': calendar_days,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
        'all_tasks': [task.to_dict() for task in tasks if not task.deadline]  # Tasks without deadline
    }
    return render(request, 'scheduler/calendar.html', context)


@login_required
def analytics(request):
    """Analytics view"""
    scheduler = get_user_scheduler(request.user)
    task_history = get_user_history(request.user)
    scheduler.recalculate_priorities()
    tasks = scheduler.get_all_tasks()
    stats = scheduler.get_stats()
    history_stats = task_history.get_stats()
    
    # Calculate additional analytics
    completed_tasks = [t for t in tasks if t.status == 'completed']
    total_effort = sum(t.estimated_effort for t in tasks)
    completed_effort = sum(t.estimated_effort for t in completed_tasks)
    remaining_effort = total_effort - completed_effort
    
    # Tasks by project - show breakdown with all statuses
    projects = {}
    for task in tasks:
        if task.project not in projects:
            projects[task.project] = {
                'total': 0, 
                'completed': 0,
                'pending': 0,
                'in_progress': 0,
                'skipped': 0
            }
        projects[task.project]['total'] += 1
        if task.status == 'completed':
            projects[task.project]['completed'] += 1
        elif task.status == 'pending':
            projects[task.project]['pending'] += 1
        elif task.status == 'in-progress':
            projects[task.project]['in_progress'] += 1
        elif task.status == 'skipped':
            projects[task.project]['skipped'] += 1
    
    context = {
        'stats': stats,
        'history_stats': history_stats,
        'total_effort': round(total_effort, 2),
        'completed_effort': round(completed_effort, 2),
        'remaining_effort': round(remaining_effort, 2),
        'projects': projects,
        'recent_history': task_history.get_recent_history(10)
    }
    return render(request, 'scheduler/analytics.html', context)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def api_add_task(request):
    """API endpoint to add a task"""
    scheduler = get_user_scheduler(request.user)
    task_history = get_user_history(request.user)
    undo_redo_manager = get_user_undo_redo(request.user)
    
    try:
        data = json.loads(request.body)
        
        # Parse deadline and make timezone-aware
        deadline = None
        if data.get('deadline'):
            try:
                deadline = datetime.fromisoformat(data['deadline'].replace('Z', '+00:00'))
                # If naive, make it timezone-aware
                if deadline.tzinfo is None:
                    deadline = timezone.make_aware(deadline)
            except (ValueError, AttributeError):
                # Try parsing without timezone info
                try:
                    deadline = datetime.strptime(data['deadline'], '%Y-%m-%dT%H:%M')
                    deadline = timezone.make_aware(deadline)
                except (ValueError, AttributeError):
                    deadline = None
        
        # Create task
        task = scheduler.add_task(
            title=data['title'],
            project=data.get('project', 'General'),
            domain=data.get('domain', 'General'),
            deadline=deadline,
            difficulty=int(data.get('difficulty', 5)),
            estimated_effort=float(data.get('estimated_effort', 1)),
            importance=int(data.get('importance', 5))
        )
        
        # Save to database
        TaskModel.objects.create(
            id=task.id,
            user=request.user,
            title=task.title,
            project=task.project,
            domain=task.domain,
            deadline=task.deadline,
            difficulty=task.difficulty,
            estimated_effort=task.estimated_effort,
            importance=task.importance,
            status=task.status,
            priority_score=task.priority_score,
            created_at=task.created_at,
            completed_at=task.completed_at
        )
        
        # Record in history
        task_history.add_entry(task.id, 'created', task.to_dict())
        undo_redo_manager.record_action({
            'type': 'add',
            'task_id': task.id,
            'task': task.to_dict()
        })
        
        return JsonResponse({'success': True, 'task': task.to_dict()})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def api_update_task(request, task_id):
    """API endpoint to update a task"""
    scheduler = get_user_scheduler(request.user)
    task_history = get_user_history(request.user)
    undo_redo_manager = get_user_undo_redo(request.user)
    
    try:
        data = json.loads(request.body)
        
        # Get old state
        task = scheduler.get_task(task_id)
        if not task:
            return JsonResponse({'success': False, 'error': 'Task not found'}, status=404)
        
        # Verify task belongs to user
        try:
            task_model = TaskModel.objects.get(id=task_id, user=request.user)
        except TaskModel.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Task not found'}, status=404)
        
        old_state = task.to_dict()
        
        # Prepare updates
        updates = {}
        if 'title' in data:
            updates['title'] = data['title']
        if 'project' in data:
            updates['project'] = data['project']
        if 'domain' in data:
            updates['domain'] = data['domain']
        if 'deadline' in data:
            deadline = None
            if data['deadline']:
                try:
                    deadline = datetime.fromisoformat(data['deadline'].replace('Z', '+00:00'))
                    if deadline.tzinfo is None:
                        deadline = timezone.make_aware(deadline)
                except (ValueError, AttributeError):
                    try:
                        deadline = datetime.strptime(data['deadline'], '%Y-%m-%dT%H:%M')
                        deadline = timezone.make_aware(deadline)
                    except (ValueError, AttributeError):
                        deadline = None
            updates['deadline'] = deadline
        if 'difficulty' in data:
            updates['difficulty'] = int(data['difficulty'])
        if 'estimated_effort' in data:
            updates['estimated_effort'] = float(data['estimated_effort'])
        if 'importance' in data:
            updates['importance'] = int(data['importance'])
        if 'status' in data:
            updates['status'] = data['status']
        
        # Update task
        result = scheduler.update_task(task_id, **updates)
        
        # Update database
        task_model.title = result['task'].title
        task_model.project = result['task'].project
        task_model.domain = result['task'].domain
        task_model.deadline = result['task'].deadline
        task_model.difficulty = result['task'].difficulty
        task_model.estimated_effort = result['task'].estimated_effort
        task_model.importance = result['task'].importance
        task_model.status = result['task'].status
        task_model.priority_score = result['task'].priority_score
        task_model.completed_at = result['task'].completed_at
        task_model.save()
        
        # Record in history
        task_history.add_entry(task_id, 'updated', result['task'].to_dict(), old_state)
        undo_redo_manager.record_action({
            'type': 'update',
            'task_id': task_id,
            'old_state': old_state,
            'new_state': result['task'].to_dict()
        })
        
        return JsonResponse({'success': True, 'task': result['task'].to_dict()})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def api_complete_task(request, task_id):
    """API endpoint to complete a task"""
    scheduler = get_user_scheduler(request.user)
    task_history = get_user_history(request.user)
    undo_redo_manager = get_user_undo_redo(request.user)
    
    try:
        # Verify task belongs to user
        try:
            task_model = TaskModel.objects.get(id=task_id, user=request.user)
        except TaskModel.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Task not found'}, status=404)
        
        result = scheduler.complete_task(task_id)
        
        # Update database
        task_model.status = 'completed'
        task_model.completed_at = timezone.now()
        task_model.save()
        
        # Record in history
        task_history.add_entry(task_id, 'completed', result['task'].to_dict(), result['old_state'])
        undo_redo_manager.record_action({
            'type': 'complete',
            'task_id': task_id,
            'old_state': result['old_state'],
            'new_state': result['task'].to_dict()
        })
        
        return JsonResponse({'success': True, 'task': result['task'].to_dict()})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def api_skip_task(request, task_id):
    """API endpoint to skip a task"""
    scheduler = get_user_scheduler(request.user)
    task_history = get_user_history(request.user)
    undo_redo_manager = get_user_undo_redo(request.user)
    
    try:
        # Verify task belongs to user
        try:
            task_model = TaskModel.objects.get(id=task_id, user=request.user)
        except TaskModel.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Task not found'}, status=404)
        
        result = scheduler.skip_task(task_id)
        
        # Update database
        task_model.status = 'skipped'
        task_model.save()
        
        # Record in history
        task_history.add_entry(task_id, 'skipped', result['task'].to_dict(), result['old_state'])
        undo_redo_manager.record_action({
            'type': 'skip',
            'task_id': task_id,
            'old_state': result['old_state'],
            'new_state': result['task'].to_dict()
        })
        
        return JsonResponse({'success': True, 'task': result['task'].to_dict()})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@csrf_exempt
@login_required
@require_http_methods(["DELETE"])
def api_delete_task(request, task_id):
    """API endpoint to delete a task"""
    scheduler = get_user_scheduler(request.user)
    task_history = get_user_history(request.user)
    undo_redo_manager = get_user_undo_redo(request.user)
    
    try:
        task = scheduler.get_task(task_id)
        if not task:
            return JsonResponse({'success': False, 'error': 'Task not found'}, status=404)
        
        # Verify task belongs to user
        try:
            task_model = TaskModel.objects.get(id=task_id, user=request.user)
        except TaskModel.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Task not found'}, status=404)
        
        old_state = task.to_dict()
        scheduler.delete_task(task_id)
        
        # Delete from database
        task_model.delete()
        
        # Record in history
        task_history.add_entry(task_id, 'deleted', None, old_state)
        undo_redo_manager.record_action({
            'type': 'delete',
            'task_id': task_id,
            'old_state': old_state
        })
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def api_undo(request):
    """API endpoint to undo last action"""
    undo_redo_manager = get_user_undo_redo(request.user)
    try:
        action = undo_redo_manager.undo()
        if not action:
            return JsonResponse({'success': False, 'error': 'Nothing to undo'})
        
        # Implement undo logic based on action type
        # This is a simplified version - in production, implement full undo logic
        return JsonResponse({'success': True, 'action': action})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def api_redo(request):
    """API endpoint to redo last undone action"""
    undo_redo_manager = get_user_undo_redo(request.user)
    try:
        action = undo_redo_manager.redo()
        if not action:
            return JsonResponse({'success': False, 'error': 'Nothing to redo'})
        
        return JsonResponse({'success': True, 'action': action})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_http_methods(["GET"])
def api_get_tasks(request):
    """API endpoint to get all tasks"""
    scheduler = get_user_scheduler(request.user)
    scheduler.recalculate_priorities()
    tasks = scheduler.get_all_tasks()
    return JsonResponse({
        'success': True,
        'tasks': [task.to_dict() for task in tasks],
        'stats': scheduler.get_stats()
    })

