from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'

# Template filters
@app.template_filter('format_datetime')
def format_datetime(value):
    if value is None:
        return ''
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace('Z', '+00:00'))
        except:
            return value
    return value.strftime('%Y-%m-%d %H:%M')

@app.template_filter('relative_time')
def relative_time(value):
    if value is None:
        return ''
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace('Z', '+00:00'))
        except:
            return value
    
    now = datetime.now()
    diff = now - value
    
    if diff.days > 0:
        return f'{diff.days}天前'
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f'{hours}小时前'
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f'{minutes}分钟前'
    else:
        return '刚刚'

# Database setup
def get_db():
    db = sqlite3.connect('todo_basic.db')
    db.row_factory = sqlite3.Row
    return db

def init_db():
    db = get_db()
    db.execute('''
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            completed BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            priority TEXT DEFAULT 'medium'
        )
    ''')
    db.commit()
    db.close()

# Routes
@app.route('/')
def index():
    db = get_db()
    todos = db.execute('SELECT * FROM todos ORDER BY created_at DESC').fetchall()
    stats = {
        'total': len(todos),
        'completed': len([t for t in todos if t['completed']]),
        'pending': len([t for t in todos if not t['completed']])
    }
    db.close()
    return render_template('index_basic.html', todos=todos, stats=stats)

@app.route('/add', methods=['POST'])
def add_todo():
    content = request.form.get('content', '').strip()
    priority = request.form.get('priority', 'medium')
    
    if not content:
        flash('Task content cannot be empty', 'error')
        return redirect(url_for('index'))
    
    db = get_db()
    db.execute('INSERT INTO todos (content, priority) VALUES (?, ?)', (content, priority))
    db.commit()
    db.close()
    
    flash('Task added successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/toggle/<int:todo_id>')
def toggle_todo(todo_id):
    db = get_db()
    todo = db.execute('SELECT * FROM todos WHERE id = ?', (todo_id,)).fetchone()
    if todo:
        new_status = 0 if todo['completed'] else 1
        db.execute('UPDATE todos SET completed = ? WHERE id = ?', (new_status, todo_id))
        db.commit()
        flash('Task status updated!', 'success')
    db.close()
    return redirect(url_for('index'))

@app.route('/delete/<int:todo_id>')
def delete_todo(todo_id):
    db = get_db()
    db.execute('DELETE FROM todos WHERE id = ?', (todo_id,))
    db.commit()
    db.close()
    flash('Task deleted!', 'success')
    return redirect(url_for('index'))

@app.route('/clear-all', methods=['POST'])
def clear_all():
    """清空所有历史信息"""
    db = get_db()
    db.execute('DELETE FROM todos')
    db.commit()
    db.close()
    flash('所有历史信息已清空！', 'info')
    return redirect(url_for('index'))

@app.route('/edit/<int:todo_id>', methods=['GET', 'POST'])
def edit_todo(todo_id):
    db = get_db()
    todo = db.execute('SELECT * FROM todos WHERE id = ?', (todo_id,)).fetchone()
    
    if request.method == 'POST':
        content = request.form.get('content', '').strip()
        priority = request.form.get('priority', 'medium')
        
        if not content:
            flash('Task content cannot be empty', 'error')
            db.close()
            return render_template('edit.html', todo=todo)
        
        db.execute('UPDATE todos SET content = ?, priority = ? WHERE id = ?', 
                  (content, priority, todo_id))
        db.commit()
        db.close()
        flash('Task updated successfully!', 'success')
        return redirect(url_for('index'))
    
    db.close()
    return render_template('edit.html', todo=todo)

if __name__ == '__main__':
    # Initialize database if it doesn't exist
    if not os.path.exists('todo_basic.db'):
        init_db()
        print("Database initialized successfully!")
    
    # 启动应用
    print("🚀 Flash Todo 应用启动中...")
    print("🌐 地址: http://0.0.0.0:5001")
    print("🔧 调试: 开启")
    print("💡 按 Ctrl+C 停止服务器")
    
    app.run(host='0.0.0.0', port=5001, debug=True)
