function openAddTaskModal() { document.getElementById('addTaskModal').style.display = 'block'; }
function closeAddTaskModal() { document.getElementById('addTaskModal').style.display = 'none'; document.getElementById('addTaskForm').reset(); }
function closeEditTaskModal() { document.getElementById('editTaskModal').style.display = 'none'; }
function editTask(taskId) { openEditTaskModal(taskId); }

function openEditTaskModal(taskId) {
    fetch('/api/tasks/').then(r => r.json()).then(data => {
        const task = data.tasks.find(t => t.id === taskId);
        if (!task) return;
        document.getElementById('editTaskId').value = task.id;
        document.getElementById('editTaskTitle').value = task.title;
        document.getElementById('editTaskProject').value = task.project;
        document.getElementById('editTaskDomain').value = task.domain;
        if (task.deadline) {
            const deadline = new Date(task.deadline);
            document.getElementById('editTaskDeadline').value = deadline.toISOString().slice(0, 16);
        }
        document.getElementById('editTaskDifficulty').value = task.difficulty;
        document.getElementById('editTaskEffort').value = task.estimated_effort;
        document.getElementById('editTaskImportance').value = task.importance;
        document.getElementById('editTaskModal').style.display = 'block';
    });
}

async function apiRequest(url, method, body = null) {
    const response = await fetch(url, { method, headers: {'Content-Type': 'application/json'}, body: body ? JSON.stringify(body) : null });
    return response.json();
}

document.getElementById('addTaskForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(e.target));
    if (data.deadline) data.deadline = new Date(data.deadline).toISOString();
    const result = await apiRequest('/api/tasks/', 'POST', data);
    if (result.success) location.reload(); else alert('Error: ' + result.error);
});

document.getElementById('editTaskForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const taskId = formData.get('task_id');
    const data = Object.fromEntries(formData);
    delete data.task_id;
    if (data.deadline) data.deadline = new Date(data.deadline).toISOString();
    const result = await apiRequest(`/api/tasks/${taskId}/`, 'POST', data);
    if (result.success) location.reload(); else alert('Error: ' + result.error);
});

async function completeTask(taskId) { const r = await apiRequest(`/api/tasks/${taskId}/complete/`, 'POST'); if (r.success) location.reload(); else alert(r.error); }
async function skipTask(taskId) { if (!confirm('Skip this task?')) return; const r = await apiRequest(`/api/tasks/${taskId}/skip/`, 'POST'); if (r.success) location.reload(); else alert(r.error); }
async function deleteTask(taskId) { if (!confirm('Delete this task?')) return; const r = await apiRequest(`/api/tasks/${taskId}/delete/`, 'DELETE'); if (r.success) location.reload(); else alert(r.error); }
async function updateTaskStatus(taskId, status) { const r = await apiRequest(`/api/tasks/${taskId}/`, 'POST', {status}); if (r.success) location.reload(); else alert(r.error); }

window.onclick = function(event) {
    const addModal = document.getElementById('addTaskModal');
    const editModal = document.getElementById('editTaskModal');
    if (event.target === addModal) closeAddTaskModal();
    if (event.target === editModal) closeEditTaskModal();
};
