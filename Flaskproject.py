from flask import Flask, render_template_string, request, jsonify, redirect, url_for
from datetime import datetime, timedelta
import json
import os

app = Flask(__name__)

tasks = []
categories = ['Work', 'Personal', 'Learning', 'Health']
task_id_counter = 1


HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Alek's Dashboard </title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
        }
        
        .header {
            text-align: center;
            margin-bottom: 40px;
        }
        
        .header h1 {
            color: #333;
            font-size: 2.5em;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            transform: translateY(0);
            transition: transform 0.3s ease;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
        }
        
        .stat-number {
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .add-task-form {
            background: #f8f9fa;
            padding: 25px;
            border-radius: 15px;
            margin-bottom: 30px;
            border: 2px solid #e9ecef;
        }
        
        .form-row {
            display: grid;
            grid-template-columns: 2fr 1fr 1fr auto;
            gap: 15px;
            align-items: end;
        }
        
        .form-group {
            display: flex;
            flex-direction: column;
        }
        
        .form-group label {
            margin-bottom: 8px;
            font-weight: 600;
            color: #495057;
        }
        
        .form-group input, .form-group select {
            padding: 12px;
            border: 2px solid #dee2e6;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s ease;
        }
        
        .form-group input:focus, .form-group select:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .tasks-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        
        .category-column {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 20px;
            min-height: 400px;
        }
        
        .category-header {
            font-size: 1.3em;
            font-weight: bold;
            margin-bottom: 20px;
            color: #495057;
            text-align: center;
            padding: 10px;
            border-radius: 8px;
        }
        
        .work { background: linear-gradient(135deg, #ff6b6b, #ee5a24); }
        .personal { background: linear-gradient(135deg, #4ecdc4, #44a08d); }
        .learning { background: linear-gradient(135deg, #45b7d1, #96c93d); }
        .health { background: linear-gradient(135deg, #f093fb, #f5576c); }
        
        .task-item {
            background: white;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }
        
        .task-item:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.15);
        }
        
        .task-item.completed {
            opacity: 0.7;
            text-decoration: line-through;
        }
        
        .task-title {
            font-weight: 600;
            margin-bottom: 8px;
            color: #333;
        }
        
        .task-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.9em;
            color: #666;
        }
        
        .task-actions {
            display: flex;
            gap: 8px;
        }
        
        .btn-sm {
            padding: 5px 10px;
            font-size: 12px;
            border-radius: 5px;
        }
        
        .btn-success { background: #28a745; color: white; }
        .btn-danger { background: #dc3545; color: white; }
        
        .priority-high { border-left-color: #dc3545; }
        .priority-medium { border-left-color: #ffc107; }
        .priority-low { border-left-color: #28a745; }
        
        @media (max-width: 768px) {
            .form-row {
                grid-template-columns: 1fr;
            }
            .tasks-container {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Alek's Dashboard</h1>
            <p>Stay organized, stay productive!</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{{ stats.total }}</div>
                <div>Total Tasks</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ stats.completed }}</div>
                <div>Completed</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ stats.pending }}</div>
                <div>Pending</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ stats.completion_rate }}%</div>
                <div>Success Rate</div>
            </div>
        </div>
        
        <div class="add-task-form">
            <form method="POST" action="/add_task">
                <div class="form-row">
                    <div class="form-group">
                        <label for="title">Task Title</label>
                        <input type="text" id="title" name="title" placeholder="What needs to be done?" required>
                    </div>
                    <div class="form-group">
                        <label for="category">Category</label>
                        <select id="category" name="category" required>
                            {% for cat in categories %}
                            <option value="{{ cat }}">{{ cat }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="priority">Priority</label>
                        <select id="priority" name="priority" required>
                            <option value="low">Low</option>
                            <option value="medium" selected>Medium</option>
                            <option value="high">High</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <button type="submit" class="btn btn-primary">Add Task</button>
                    </div>
                </div>
            </form>
        </div>
        
        <div class="tasks-container">
            {% for category in categories %}
            <div class="category-column">
                <div class="category-header {{ category.lower() }}">
                    {{ category }} ({{ category_counts[category] }})
                </div>
                {% for task in tasks %}
                {% if task.category == category %}
                <div class="task-item priority-{{ task.priority }} {% if task.completed %}completed{% endif %}">
                    <div class="task-title">{{ task.title }}</div>
                    <div class="task-meta">
                        <span>{{ task.created_at.strftime('%m/%d %H:%M') }}</span>
                        <div class="task-actions">
                            {% if not task.completed %}
                            <form method="POST" action="/complete_task/{{ task.id }}" style="display: inline;">
                                <button type="submit" class="btn btn-success btn-sm">✓</button>
                            </form>
                            
                            {% endif %}
                            <form method="POST" action="/delete_task/{{ task.id }}" style="display: inline;">
                                <button type="submit" class="btn btn-danger btn-sm">✗</button>
                            </form>
                        </div>
                    </div>
                </div>
                {% endif %}
                {% endfor %}
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
'''

class Task:
    def __init__(self, id, title, category, priority='medium', due_date=None):
        self.id = id
        self.title = title
        self.category = category
        self.priority = priority
        self.completed = False
        self.created_at = datetime.now()
        self.due_date = datetime.strptime(due_date, '%Y-%m-%d') if due_date else None

@app.route('/')
def dashboard():
    sort_by = request.args.get('sort', 'created_at')

    sorted_tasks = sorted(
        tasks,
        key=lambda t: getattr(t, sort_by) if getattr(t, sort_by) is not None else datetime.max
    )

    total_tasks = len(sorted_tasks)
    completed_tasks = len([t for t in sorted_tasks if t.completed])
    pending_tasks = total_tasks - completed_tasks
    completion_rate = int((completed_tasks / total_tasks * 100)) if total_tasks > 0 else 0

    category_counts = {cat: len([t for t in sorted_tasks if t.category == cat]) for cat in categories}

    stats = {
        'total': total_tasks,
        'completed': completed_tasks,
        'pending': pending_tasks,
        'completion_rate': completion_rate
    }

    return render_template_string(HTML_TEMPLATE,
                                  tasks=sorted_tasks,
                                  categories=categories,
                                  stats=stats,
                                  category_counts=category_counts)

@app.route('/add_task', methods=['POST'])
def add_task():
    global task_id_counter

    title = request.form['title']
    category = request.form['category']
    priority = request.form['priority']
    due_date = request.form.get('due_date')

    new_task = Task(task_id_counter, title, category, priority, due_date)
    tasks.append(new_task)
    task_id_counter += 1

    return redirect(url_for('dashboard'))

@app.route('/complete_task/<int:task_id>', methods=['POST'])
def complete_task(task_id):
    task = next((t for t in tasks if t.id == task_id), None)
    if task:
        task.completed = True
    return redirect(url_for('dashboard'))

@app.route('/delete_task/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    global tasks
    tasks = [t for t in tasks if t.id != task_id]
    return redirect(url_for('dashboard'))

@app.route('/toggle_task/<int:task_id>', methods=['POST'])
def toggle_task(task_id):
    task = next((t for t in tasks if t.id == task_id), None)
    if task:
        task.completed = not task.completed
        return jsonify({'status': 'success', 'completed': task.completed})
    return jsonify({'status': 'error', 'message': 'Task not found'}), 404

@app.route('/api/tasks')
def get_tasks():
    return jsonify([{
        'id': t.id,
        'title': t.title,
        'category': t.category,
        'priority': t.priority,
        'completed': t.completed,
        'created_at': t.created_at.isoformat(),
        'due_date': t.due_date.strftime('%Y-%m-%d') if t.due_date else None
    } for t in tasks])

if __name__ == '__main__':
    sample_tasks = [
        Task(1, "Review project proposal", "Work", "high", (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')),
        Task(2, "Morning workout", "Health", "medium", (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')),
        Task(3, "Learn Flask advanced features", "Learning", "medium"),
        Task(4, "Buy groceries", "Personal", "low", (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')),
        Task(5, "Prepare presentation", "Work", "high", (datetime.now() + timedelta(days=4)).strftime('%Y-%m-%d')),
    ]

    tasks.extend(sample_tasks)
    task_id_counter = 6

    app.run(debug=True, host='0.0.0.0', port=5000)