# Quick Setup Guide

## Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Run Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

## Step 3: (Optional) Create Admin User

```bash
python manage.py createsuperuser
```

## Step 4: Start the Server

```bash
python manage.py runserver
```

## Step 5: Access the Application

Open your browser and navigate to:
- **Main Application**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/ (if you created a superuser)

## Troubleshooting

### Issue: Module not found errors
**Solution**: Make sure you're in the project root directory and have activated your virtual environment.

### Issue: Database errors
**Solution**: Run migrations again:
```bash
python manage.py makemigrations scheduler
python manage.py migrate
```

### Issue: Static files not loading
**Solution**: Collect static files (for production):
```bash
python manage.py collectstatic
```

### Issue: Port already in use
**Solution**: Use a different port:
```bash
python manage.py runserver 8001
```

## First Steps

1. Go to the Dashboard
2. Click "Add Task" to create your first task
3. Fill in the task details:
   - Title (required)
   - Project/Domain
   - Deadline (optional)
   - Difficulty (1-10)
   - Estimated Effort (hours)
   - Importance (1-10)
4. The system will automatically calculate the priority score
5. View tasks sorted by priority on the dashboard
6. Check the Calendar view to see tasks by deadline
7. Visit Analytics to track your productivity

## Features to Try

- **Add Multiple Tasks**: Create several tasks with different deadlines and importance levels
- **Update Priorities**: Edit tasks to see how priority scores change
- **Complete Tasks**: Mark tasks as completed to see them move out of the priority queue
- **Calendar View**: See how tasks are distributed across dates
- **Analytics**: Track your progress and productivity metrics

