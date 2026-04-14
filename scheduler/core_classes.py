"""
Core OOP Classes: Task, Scheduler, WorkSession, UndoRedoManager, TaskHistory
"""
import uuid
from datetime import datetime, timedelta
from django.utils import timezone
from .data_structures import PriorityQueue, Stack, Queue, LinkedList, STRATEGY_COMPLEXITY
from .c_core_adapter import order_tasks as c_order_tasks


class Task:
    """Task class representing a single task with all its attributes"""
    
    def __init__(self, title, project=None, domain=None, deadline=None, 
                 difficulty=5, estimated_effort=1, importance=5, 
                 status='pending', task_id=None, created_at=None, completed_at=None):
        self.id = task_id or str(uuid.uuid4())
        self.title = title
        self.project = project or 'General'
        self.domain = domain or 'General'
        self.deadline = deadline
        self.difficulty = difficulty  # 1-10 scale
        self.estimated_effort = estimated_effort  # in hours
        self.importance = importance  # 1-10 scale
        self.status = status  # 'pending', 'in-progress', 'completed', 'skipped'
        self.created_at = created_at or timezone.now()
        self.completed_at = completed_at
        self.priority_score = self.calculate_priority_score()
    
    def calculate_priority_score(self):
        """Calculate dynamic priority score based on multiple factors
        Lower score = higher priority
        """
        score = 0
        
        # Deadline urgency factor (0-100, lower is more urgent)
        if self.deadline:
            if isinstance(self.deadline, str):
                deadline = datetime.fromisoformat(self.deadline.replace('Z', '+00:00'))
                # Make timezone-aware if it's naive
                if deadline.tzinfo is None:
                    deadline = timezone.make_aware(deadline)
            else:
                deadline = self.deadline
                # Make timezone-aware if it's naive
                if deadline.tzinfo is None:
                    deadline = timezone.make_aware(deadline)
            
            now = timezone.now()
            time_until_deadline = deadline - now
            days_until_deadline = time_until_deadline.total_seconds() / (24 * 3600)
            
            if days_until_deadline < 0:
                # Overdue tasks get highest priority
                score += 0
            elif days_until_deadline <= 1:
                # Due today or tomorrow
                score += 10
            elif days_until_deadline <= 3:
                # Due within 3 days
                score += 30
            elif days_until_deadline <= 7:
                # Due within a week
                score += 50
            else:
                # More than a week away
                score += 70
        else:
            # No deadline = lower priority
            score += 80
        
        # Importance factor (1-10, inverted so higher importance = lower score)
        score += (11 - self.importance) * 5
        
        # Difficulty factor (1-10, higher difficulty = slightly lower priority for balance)
        score += self.difficulty * 2
        
        # Estimated effort factor (longer tasks get slightly lower priority)
        score += min(self.estimated_effort * 1.5, 20)
        
        return round(score, 2)
    
    def update(self, **updates):
        """Update task attributes and recalculate priority"""
        old_state = self.to_dict()
        
        if 'title' in updates:
            self.title = updates['title']
        if 'project' in updates:
            self.project = updates['project']
        if 'domain' in updates:
            self.domain = updates['domain']
        if 'deadline' in updates:
            self.deadline = updates['deadline']
        if 'difficulty' in updates:
            self.difficulty = updates['difficulty']
        if 'estimated_effort' in updates:
            self.estimated_effort = updates['estimated_effort']
        if 'importance' in updates:
            self.importance = updates['importance']
        if 'status' in updates:
            self.status = updates['status']
            if updates['status'] == 'completed' and not self.completed_at:
                self.completed_at = timezone.now()
            elif updates['status'] != 'completed':
                self.completed_at = None
        
        # Recalculate priority score
        self.priority_score = self.calculate_priority_score()
        
        return old_state
    
    def complete(self):
        """Mark task as completed"""
        return self.update(status='completed')
    
    def skip(self):
        """Mark task as skipped"""
        return self.update(status='skipped')
    
    def to_dict(self):
        """Convert task to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'project': self.project,
            'domain': self.domain,
            'deadline': self.deadline.isoformat() if isinstance(self.deadline, datetime) else self.deadline,
            'difficulty': self.difficulty,
            'estimated_effort': self.estimated_effort,
            'importance': self.importance,
            'status': self.status,
            'priority_score': self.priority_score,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'completed_at': self.completed_at.isoformat() if isinstance(self.completed_at, datetime) else (self.completed_at if self.completed_at else None)
        }


class Scheduler:
    """Scheduler class - Core scheduling logic and strategy selection."""

    def __init__(self):
        self.priority_queue = PriorityQueue()
        self.tasks = {}  # Store all tasks by ID for quick lookup
        self.strategy = 'priority'
    
    def add_task(self, **task_data):
        """Add a new task to the scheduler"""
        task = Task(**task_data)
        self.tasks[task.id] = task
        self.priority_queue.enqueue(task)
        return task
    
    def set_strategy(self, strategy):
        """Set active scheduling strategy."""
        if strategy in STRATEGY_COMPLEXITY:
            self.strategy = strategy

    def get_next_task(self):
        """Get the next task based on the selected strategy."""
        pending_tasks = [t for t in self.tasks.values() if t.status in ('pending', 'in-progress')]
        if not pending_tasks:
            return None
        ordered = c_order_tasks(self.strategy, pending_tasks)
        return ordered[0] if ordered else None
    
    def dequeue_next_task(self):
        """Remove and return the next highest priority task"""
        task = self.priority_queue.dequeue()
        if task:
            del self.tasks[task.id]
        return task
    
    def update_task(self, task_id, **updates):
        """Update a task and rebuild the priority queue"""
        task = self.tasks.get(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} not found")
        
        old_state = task.update(**updates)
        
        # Rebuild the priority queue to reflect updated priorities
        self.priority_queue.rebuild()
        
        return {'task': task, 'old_state': old_state}
    
    def complete_task(self, task_id):
        """Complete a task"""
        task = self.tasks.get(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} not found")
        
        old_state = task.complete()
        self.priority_queue.remove(task_id)
        
        return {'task': task, 'old_state': old_state}
    
    def skip_task(self, task_id):
        """Skip a task"""
        task = self.tasks.get(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} not found")
        
        old_state = task.skip()
        self.priority_queue.remove(task_id)
        
        return {'task': task, 'old_state': old_state}
    
    def delete_task(self, task_id):
        """Delete a task"""
        task = self.tasks.get(task_id)
        if not task:
            return False
        
        del self.tasks[task_id]
        self.priority_queue.remove(task_id)
        
        return True
    
    def get_all_tasks(self):
        """Get all tasks in the selected strategy order."""
        active = [t for t in self.tasks.values() if t.status in ('pending', 'in-progress')]
        done = [t for t in self.tasks.values() if t.status not in ('pending', 'in-progress')]

        ordered_active = c_order_tasks(self.strategy, active)
        ordered_done = c_order_tasks('lifo', done)
        return ordered_active + ordered_done
    
    def get_task(self, task_id):
        """Get a task by ID"""
        return self.tasks.get(task_id)
    
    def get_tasks_by_status(self, status):
        """Get tasks by status"""
        return [task for task in self.get_all_tasks() if task.status == status]
    
    def get_tasks_by_project(self, project):
        """Get tasks by project"""
        return [task for task in self.get_all_tasks() if task.project == project]
    
    def recalculate_priorities(self):
        """Recalculate all priorities (useful when time passes)"""
        for task in self.tasks.values():
            task.priority_score = task.calculate_priority_score()
        self.priority_queue.rebuild()
    
    def get_stats(self):
        """Get statistics"""
        all_tasks = self.get_all_tasks()
        pending = len([t for t in all_tasks if t.status == 'pending'])
        in_progress = len([t for t in all_tasks if t.status == 'in-progress'])
        completed = len([t for t in all_tasks if t.status == 'completed'])
        skipped = len([t for t in all_tasks if t.status == 'skipped'])
        
        avg_priority = sum(t.priority_score for t in all_tasks) / len(all_tasks) if all_tasks else 0
        
        return {
            'total': len(all_tasks),
            'pending': pending,
            'in_progress': in_progress,
            'completed': completed,
            'skipped': skipped,
            'average_priority': round(avg_priority, 2),
            'strategy': self.strategy,
            'strategy_meta': STRATEGY_COMPLEXITY[self.strategy],
        }


class WorkSession:
    """WorkSession class - Manages daily work sessions using a queue"""
    
    def __init__(self, date=None):
        if date is None:
            date = datetime.now()
        elif isinstance(date, str):
            date = datetime.fromisoformat(date)
        
        self.id = date.strftime('%Y-%m-%d')  # Use date as ID (YYYY-MM-DD)
        self.date = date
        self.task_queue = Queue()
        self.completed_tasks = []
        self.created_at = timezone.now()
    
    def add_task(self, task):
        """Add a task to the work session queue"""
        if not isinstance(task, Task):
            raise ValueError('Invalid task object')
        self.task_queue.enqueue(task)
        return True
    
    def get_next_task(self):
        """Get the next task in the session"""
        return self.task_queue.front()
    
    def start_next_task(self):
        """Start working on the next task"""
        task = self.task_queue.dequeue()
        if task:
            task.update(status='in-progress')
        return task
    
    def complete_task(self, task_id):
        """Complete a task in the session"""
        # Check if task is in queue
        tasks = self.task_queue.to_array()
        task = next((t for t in tasks if t.id == task_id), None)
        if task:
            self.task_queue.remove(task_id)
            task.complete()
            self.completed_tasks.append(task)
            return task
        return None
    
    def remove_task(self, task_id):
        """Remove a task from the session"""
        return self.task_queue.remove(task_id)
    
    def get_all_tasks(self):
        """Get all tasks in the session"""
        return self.task_queue.to_array()
    
    def get_completed_tasks(self):
        """Get completed tasks"""
        return self.completed_tasks
    
    def get_stats(self):
        """Get session statistics"""
        total_tasks = self.task_queue.size() + len(self.completed_tasks)
        completed = len(self.completed_tasks)
        remaining = self.task_queue.size()
        completion_rate = (completed / total_tasks * 100) if total_tasks > 0 else 0
        
        all_session_tasks = list(self.task_queue.to_array()) + self.completed_tasks
        total_effort = sum(task.estimated_effort for task in all_session_tasks)
        completed_effort = sum(task.estimated_effort for task in self.completed_tasks)
        
        return {
            'date': self.id,
            'total_tasks': total_tasks,
            'completed': completed,
            'remaining': remaining,
            'completion_rate': round(completion_rate, 2),
            'total_effort': round(total_effort, 2),
            'completed_effort': round(completed_effort, 2)
        }
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'date': self.date.isoformat(),
            'tasks': [task.to_dict() for task in self.task_queue.to_array()],
            'completed_tasks': [task.to_dict() for task in self.completed_tasks],
            'stats': self.get_stats()
        }


class UndoRedoManager:
    """UndoRedoManager class - Manages undo/redo operations using stacks"""
    
    def __init__(self):
        self.undo_stack = Stack()
        self.redo_stack = Stack()
    
    def record_action(self, action):
        """Record an action for undo"""
        self.undo_stack.push(action)
        # Clear redo stack when a new action is recorded
        self.redo_stack.clear()
    
    def undo(self):
        """Undo the last action"""
        if self.undo_stack.is_empty():
            return None
        
        action = self.undo_stack.pop()
        self.redo_stack.push(action)
        return action
    
    def redo(self):
        """Redo the last undone action"""
        if self.redo_stack.is_empty():
            return None
        
        action = self.redo_stack.pop()
        self.undo_stack.push(action)
        return action
    
    def can_undo(self):
        """Check if undo is available"""
        return not self.undo_stack.is_empty()
    
    def can_redo(self):
        """Check if redo is available"""
        return not self.redo_stack.is_empty()
    
    def clear(self):
        """Clear both stacks"""
        self.undo_stack.clear()
        self.redo_stack.clear()


class TaskHistory:
    """TaskHistory class - Maintains task history using a linked list"""
    
    def __init__(self):
        self.history = LinkedList()
    
    def add_entry(self, task_id, action, task_data, previous_state=None):
        """Add a history entry"""
        history_entry = {
            'id': str(uuid.uuid4()),
            'task_id': task_id,
            'action': action,  # 'created', 'updated', 'completed', 'skipped', 'deleted'
            'timestamp': datetime.now(),
            'task_data': task_data,
            'previous_state': previous_state
        }
        
        self.history.prepend(history_entry)  # Add to front (most recent first)
        return history_entry
    
    def get_task_history(self, task_id):
        """Get history for a specific task"""
        return [entry for entry in self.history.to_array() if entry['task_id'] == task_id]
    
    def get_all_history(self):
        """Get all history entries"""
        return self.history.to_array()
    
    def get_recent_history(self, limit=10):
        """Get recent history (last N entries)"""
        return self.history.to_array()[:limit]
    
    def get_history_by_action(self, action):
        """Get history by action type"""
        return [entry for entry in self.history.to_array() if entry['action'] == action]
    
    def get_history_by_date_range(self, start_date, end_date):
        """Get history for a date range"""
        start = datetime.fromisoformat(start_date) if isinstance(start_date, str) else start_date
        end = datetime.fromisoformat(end_date) if isinstance(end_date, str) else end_date
        
        return [
            entry for entry in self.history.to_array()
            if start <= entry['timestamp'] <= end
        ]
    
    def clear(self):
        """Clear history"""
        self.history.clear()
    
    def get_stats(self):
        """Get history statistics"""
        all_entries = self.history.to_array()
        actions = {}
        
        for entry in all_entries:
            action = entry['action']
            actions[action] = actions.get(action, 0) + 1
        
        return {
            'total_entries': len(all_entries),
            'actions': actions,
            'oldest_entry': all_entries[-1]['timestamp'] if all_entries else None,
            'newest_entry': all_entries[0]['timestamp'] if all_entries else None
        }

