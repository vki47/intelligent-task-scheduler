# Priority Task Scheduler

A web-based productivity application designed to help professionals decide what to work on next using dynamic priority scoring and intelligent task scheduling.

## Features

- **Dynamic Priority Scoring**: Tasks are automatically prioritized based on deadline urgency, complexity, and importance
- **Priority Queue (Min-Heap)**: Most urgent tasks are always surfaced first
- **Work Sessions**: Organize tasks into daily work sessions
- **Undo/Redo**: Full undo/redo functionality for task management
- **Task History**: Complete history tracking using linked lists
- **Dashboard**: Overview of all tasks and priorities
- **Calendar View**: Visualize tasks by deadline
- **Analytics**: Track productivity and workload patterns

## Technical Architecture

### Data Structures
- **Priority Queue (Min-Heap)**: For efficient task scheduling
- **Stack**: For undo/redo operations
- **Queue**: For daily work sessions
- **Linked List**: For task history tracking

### Object-Oriented Design
- `Task`: Represents individual tasks with attributes
- `PriorityQueue`: Min-heap implementation for task scheduling
- `Scheduler`: Core scheduling logic and priority calculation
- `WorkSession`: Manages daily work sessions
- `UndoRedoManager`: Handles undo/redo operations
- `TaskHistory`: Maintains task history using linked lists

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd "hackathon for aat"
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run database migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. Create a superuser (optional, for admin access):
   ```bash
   python manage.py createsuperuser
   ```

6. Start the development server:
   ```bash
   python manage.py runserver
   ```

7. Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser

### Production Deployment

For production, configure:
- Set `DEBUG = False` in `settings.py`
- Update `SECRET_KEY` with a secure key
- Configure proper database (PostgreSQL recommended)
- Set up static files collection
- Use a production WSGI server (e.g., Gunicorn)

## Project Structure

```
.
├── task_scheduler/          # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── scheduler/               # Main Django app
│   ├── models.py           # Django models
│   ├── views.py            # View functions
│   ├── urls.py             # URL routing
│   ├── data_structures.py  # Core data structures (PriorityQueue, Stack, Queue, LinkedList)
│   └── core_classes.py     # OOP classes (Task, Scheduler, WorkSession, etc.)
├── templates/              # HTML templates
│   ├── base.html
│   └── scheduler/
│       ├── dashboard.html
│       ├── calendar.html
│       └── analytics.html
├── static/                # Static files (CSS, JS)
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
├── manage.py              # Django management script
└── requirements.txt       # Python dependencies
```

## Usage

1. **Add Tasks**: Click "Add Task" and fill in the task details:
   - Title (required)
   - Project/Domain
   - Deadline (optional)
   - Difficulty Level (1-10)
   - Estimated Effort (hours)
   - Importance (1-10)

2. **View Priority Queue**: The dashboard automatically shows tasks sorted by priority (lower score = higher priority)

3. **Manage Tasks**: 
   - Complete tasks when finished
   - Skip tasks you don't want to do
   - Edit task details to update priorities
   - Delete tasks you no longer need

4. **Calendar View**: See all tasks organized by their deadlines

5. **Analytics**: Track your productivity with detailed statistics and insights

## Priority Score Calculation

The priority score is calculated using:
- **Deadline Urgency**: Overdue tasks get highest priority, followed by tasks due soon
- **Importance**: Higher importance = lower score (higher priority)
- **Difficulty**: More complex tasks get slightly adjusted scores
- **Estimated Effort**: Longer tasks get slightly lower priority

**Lower score = Higher priority**

## Technologies

- **Backend**: Django 4.2+
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla JS)
- **Database**: SQLite (development), PostgreSQL (production recommended)
- **Data Structures**: Custom Python implementations of:
  - Priority Queue (Min-Heap)
  - Stack
  - Queue
  - Linked List

## API Endpoints

- `GET /` - Dashboard view
- `GET /dashboard/` - Dashboard view
- `GET /calendar/` - Calendar view
- `GET /analytics/` - Analytics view
- `POST /api/tasks/` - Add new task
- `POST /api/tasks/<id>/` - Update task
- `POST /api/tasks/<id>/complete/` - Complete task
- `POST /api/tasks/<id>/skip/` - Skip task
- `DELETE /api/tasks/<id>/delete/` - Delete task
- `GET /api/tasks/` - Get all tasks
- `POST /api/undo/` - Undo last action
- `POST /api/redo/` - Redo last undone action

## Contributing

This is a hackathon project demonstrating:
- Object-Oriented Programming (OOP) principles
- Data Structures and Algorithms (DSA)
- Full-stack web development
- Django framework usage

## License

MIT License
