from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import os

# Initialize Flask app
app = Flask(__name__)

# Basic configuration
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo_simple.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Simple Todo model
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    priority = db.Column(db.String(20), default='medium')

    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'completed': self.completed,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'priority': self.priority
        }

# Routes
@app.route('/')
def index():
    todos = Todo.query.order_by(Todo.created_at.desc()).all()
    stats = {
        'total': len(todos),
        'completed': len([t for t in todos if t.completed]),
        'pending': len([t for t in todos if not t.completed])
    }
    return render_template('index.html', todos=todos, stats=stats)

@app.route('/add', methods=['POST'])
def add_todo():
    content = request.form.get('content', '').strip()
    priority = request.form.get('priority', 'medium')
    
    if not content:
        flash('Task content cannot be empty', 'error')
        return redirect(url_for('index'))
    
    todo = Todo(content=content, priority=priority)
    db.session.add(todo)
    db.session.commit()
    
    flash('Task added successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/toggle/<int:todo_id>')
def toggle_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    todo.completed = not todo.completed
    db.session.commit()
    flash('Task status updated!', 'success')
    return redirect(url_for('index'))

@app.route('/delete/<int:todo_id>')
def delete_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    db.session.delete(todo)
    db.session.commit()
    flash('Task deleted!', 'success')
    return redirect(url_for('index'))

@app.route('/edit/<int:todo_id>', methods=['GET', 'POST'])
def edit_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    
    if request.method == 'POST':
        content = request.form.get('content', '').strip()
        priority = request.form.get('priority', 'medium')
        
        if not content:
            flash('Task content cannot be empty', 'error')
            return render_template('edit.html', todo=todo)
        
        todo.content = content
        todo.priority = priority
        db.session.commit()
        flash('Task updated successfully!', 'success')
        return redirect(url_for('index'))
    
    return render_template('edit.html', todo=todo)

# API routes
@app.route('/api/todos')
def api_todos():
    todos = Todo.query.order_by(Todo.created_at.desc()).all()
    return jsonify([todo.to_dict() for todo in todos])

@app.route('/api/todos', methods=['POST'])
def api_add_todo():
    data = request.get_json()
    content = data.get('content', '').strip()
    priority = data.get('priority', 'medium')
    
    if not content:
        return jsonify({'error': 'Task content cannot be empty'}), 400
    
    todo = Todo(content=content, priority=priority)
    db.session.add(todo)
    db.session.commit()
    
    return jsonify(todo.to_dict()), 201

@app.route('/api/todos/<int:todo_id>', methods=['PUT'])
def api_update_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    data = request.get_json()
    
    if 'content' in data:
        content = data['content'].strip()
        if not content:
            return jsonify({'error': 'Task content cannot be empty'}), 400
        todo.content = content
    
    if 'completed' in data:
        todo.completed = data['completed']
    
    if 'priority' in data:
        todo.priority = data['priority']
    
    db.session.commit()
    return jsonify(todo.to_dict())

@app.route('/api/todos/<int:todo_id>', methods=['DELETE'])
def api_delete_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    db.session.delete(todo)
    db.session.commit()
    return '', 204

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

@app.errorhandler(413)
def too_large(error):
    return jsonify({'error': 'Request entity too large'}), 413

# Create database tables
def init_db():
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")

if __name__ == '__main__':
    # Initialize database if it doesn't exist
    if not os.path.exists('todo_simple.db'):
        init_db()
    
    app.run(debug=True, host='0.0.0.0', port=5000) 
    app.run(
        host=args.host,
        port=args.port,
        debug=args.debug,
        host='0.0.0.0',
        port=5000,
        debug=True,
        host='0.0.0.0',
        port=5000,
    )