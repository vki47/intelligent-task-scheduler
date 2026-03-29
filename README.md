# Priority Task Scheduler

A polished Django + DSA mini-project that demonstrates how different task scheduling strategies change execution order, wait time, and performance.

## Features

- Multiple scheduling strategies: **FIFO (Queue)**, **LIFO (Stack)**, and **Priority (Min-Heap)**.
- Dashboard strategy selector with real-time explanation of data structure and complexity.
- Comparison dashboard for average wait time, completed task count, and operation complexities.
- Heap visualization page with binary-tree rendering and array index representation.
- Demo mode to auto-populate varied sample tasks for classroom/demo walkthroughs.
- Calendar and analytics pages for productivity tracking.

## DSA Concepts Used

- **Queue (FIFO):** First task added is first to execute.
- **Stack (LIFO):** Most recently added task executes first.
- **Min-Heap Priority Queue:** Task with smallest priority score executes first.
- **Linked List:** Stores task history entries.
- **Stack Pair:** Undo/redo simulation using two stacks.

## Scheduling Strategies Explained

### 1) FIFO Scheduling (Queue)
- Best for fairness and preserving arrival order.
- Insert: O(1), Remove: O(1), Peek: O(1).

### 2) LIFO Scheduling (Stack)
- Best when newest items are most relevant (short-term context switching).
- Insert: O(1), Remove: O(1), Peek: O(1).

### 3) Priority Scheduling (Min-Heap)
- Best when urgency matters (deadline + importance + effort based score).
- Insert: O(log n), Remove: O(log n), Peek: O(1).

## Time & Space Complexity Analysis

| Strategy | DS Used | Insert | Remove | Peek | Space |
|---|---|---:|---:|---:|---:|
| FIFO | Queue | O(1) | O(1) | O(1) | O(n) |
| LIFO | Stack | O(1) | O(1) | O(1) | O(n) |
| Priority | Min-Heap | O(log n) | O(log n) | O(1) | O(n) |

Average wait time is estimated by simulating each strategy over current pending tasks and summing elapsed effort-hours before each completion.

## Setup Instructions

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run migrations:
   ```bash
   python manage.py migrate
   ```
3. Start server:
   ```bash
   python manage.py runserver
   ```

## Key Pages

- `/dashboard/` – strategy selector, DSA explanation, demo mode, live comparison snapshot.
- `/analytics/` – productivity insights + strategy comparison dashboard.
- `/heap/` – binary tree visualization for current min-heap state.

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

This is a project demonstrating:
- Object-Oriented Programming (OOP) principles
- Data Structures and Algorithms (DSA)
- Full-stack web development
- Django framework usage

## License

MIT License
