from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# 数据库文件路径
DATABASE = 'todo.db'

def format_datetime(datetime_str):
    """格式化时间字符串为可读格式"""
    if not datetime_str:
        return None
    try:
        dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        return dt.strftime('%Y年%m月%d日 %H:%M')
    except:
        return datetime_str

def get_relative_time(datetime_str):
    """获取相对时间(如:2小时前)"""
    if not datetime_str:
        return None
    try:
        dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        now = datetime.now()
        diff = now - dt
        
        if diff.days > 0:
            return f"{diff.days}天前"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours}小时前"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes}分钟前"
        else:
            return "刚刚"
    except:
        return None

# 注册模板过滤器
app.jinja_env.filters['format_datetime'] = format_datetime
app.jinja_env.filters['relative_time'] = get_relative_time

def init_db():
    """初始化数据库"""
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                completed BOOLEAN DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                completed_at TEXT NULL,
                priority TEXT DEFAULT 'medium'
            )
        ''')
        conn.commit()

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # 使结果可以像字典一样访问
    return conn

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        content = request.form.get("content", "").strip()
        priority = request.form.get("priority", "medium")
        
        if content:
            conn = get_db_connection()
            conn.execute(
                "INSERT INTO todos (content, priority) VALUES (?, ?)",
                (content, priority)
            )
            conn.commit()
            conn.close()
            flash("任务添加成功！", "success")
        else:
            flash("任务内容不能为空！", "error")
        
        return redirect(url_for("index"))
    
    # 获取所有任务并排序
    conn = get_db_connection()
    todos = conn.execute('''
        SELECT * FROM todos 
        ORDER BY 
            completed ASC,
            CASE priority 
                WHEN 'high' THEN 1 
                WHEN 'medium' THEN 2 
                WHEN 'low' THEN 3 
                ELSE 2 
            END ASC,
            created_at ASC
    ''').fetchall()
    conn.close()
    
    return render_template("index.html", todos=todos)

@app.route("/complete/<int:todo_id>")
def complete(todo_id):
    conn = get_db_connection()
    conn.execute(
        "UPDATE todos SET completed = 1, completed_at = ? WHERE id = ?",
        (datetime.now().isoformat(), todo_id)
    )
    conn.commit()
    conn.close()
    flash("任务已标记为完成！", "success")
    return redirect(url_for("index"))

@app.route("/uncomplete/<int:todo_id>")
def uncomplete(todo_id):
    conn = get_db_connection()
    conn.execute(
        "UPDATE todos SET completed = 0, completed_at = NULL WHERE id = ?",
        (todo_id,)
    )
    conn.commit()
    conn.close()
    flash("任务已标记为未完成！", "info")
    return redirect(url_for("index"))

@app.route("/delete/<int:todo_id>")
def delete(todo_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    conn.commit()
    conn.close()
    flash("任务已删除！", "info")
    return redirect(url_for("index"))

@app.route("/edit/<int:todo_id>", methods=["GET", "POST"])
def edit(todo_id):
    conn = get_db_connection()
    
    if request.method == "POST":
        content = request.form.get("content", "").strip()
        priority = request.form.get("priority", "medium")
        
        if content:
            conn.execute(
                "UPDATE todos SET content = ?, priority = ? WHERE id = ?",
                (content, priority, todo_id)
            )
            conn.commit()
            conn.close()
            flash("任务更新成功！", "success")
            return redirect(url_for("index"))
        else:
            flash("任务内容不能为空！", "error")
    
    todo = conn.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
    conn.close()
    
    if todo is None:
        flash("任务不存在！", "error")
        return redirect(url_for("index"))
    
    return render_template("edit.html", todo=todo)

@app.route("/api/stats")
def api_stats():
    """获取任务统计信息"""
    conn = get_db_connection()
    total = conn.execute("SELECT COUNT(*) FROM todos").fetchone()[0]
    completed = conn.execute("SELECT COUNT(*) FROM todos WHERE completed = 1").fetchone()[0]
    conn.close()
    
    pending = total - completed
    completion_rate = round((completed / total * 100) if total > 0 else 0, 1)
    
    return jsonify({
        "total": total,
        "completed": completed,
        "pending": pending,
        "completion_rate": completion_rate
    })

@app.route("/api/times")
def api_times():
    """获取所有任务的格式化时间信息"""
    conn = get_db_connection()
    todos = conn.execute("SELECT id, created_at, completed_at FROM todos").fetchall()
    conn.close()
    
    times_data = {}
    for todo in todos:
        times_data[todo['id']] = {
            'created_formatted': format_datetime(todo['created_at']),
            'created_relative': get_relative_time(todo['created_at']),
            'completed_formatted': format_datetime(todo['completed_at']) if todo['completed_at'] else None,
            'completed_relative': get_relative_time(todo['completed_at']) if todo['completed_at'] else None
        }
    
    return jsonify(times_data)

@app.errorhandler(404)
def not_found(error):
    flash("请求的页面不存在！", "error")
    return redirect(url_for("index"))

if __name__ == "__main__":
    # 初始化数据库
    init_db()
    print("🚀 Flask Todo 应用启动中...")
    print("📱 访问地址: http://localhost:5000")
    print("💡 按 Ctrl+C 停止服务器")
    app.run(debug=True, host='0.0.0.0', port=5000)      
    







