from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.ext.hybrid import hybrid_property
import enum

db = SQLAlchemy()

class Priority(enum.Enum):
    """任务优先级枚举"""
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'

class Todo(db.Model):
    """Todo任务模型"""
    __tablename__ = 'todos'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    priority = db.Column(db.String(10), default=Priority.MEDIUM.value)
    due_date = db.Column(db.DateTime, nullable=True)
    tags = db.Column(db.Text, nullable=True)  # 存储为JSON字符串
    notes = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=True)
    estimated_time = db.Column(db.Integer, nullable=True)  # 预估时间（分钟）
    actual_time = db.Column(db.Integer, nullable=True)  # 实际用时（分钟）
    
    def __repr__(self):
        return f'<Todo {self.id}: {self.content[:50]}>'
    
    @hybrid_property
    def is_overdue(self):
        """检查任务是否逾期"""
        if self.due_date and not self.completed:
            return datetime.utcnow() > self.due_date
        return False
    
    @hybrid_property
    def days_until_due(self):
        """距离截止日期的天数"""
        if self.due_date and not self.completed:
            delta = self.due_date - datetime.utcnow()
            return delta.days
        return None
    
    @hybrid_property
    def completion_time(self):
        """任务完成用时（分钟）"""
        if self.completed and self.completed_at and self.created_at:
            delta = self.completed_at - self.created_at
            return int(delta.total_seconds() / 60)
        return None
    
    def mark_completed(self):
        """标记任务为完成"""
        self.completed = True
        self.completed_at = datetime.utcnow()
    
    def mark_incomplete(self):
        """标记任务为未完成"""
        self.completed = False
        self.completed_at = None
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'content': self.content,
            'completed': self.completed,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'priority': self.priority,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'tags': self.tags,
            'notes': self.notes,
            'category': self.category,
            'estimated_time': self.estimated_time,
            'actual_time': self.actual_time,
            'is_overdue': self.is_overdue,
            'days_until_due': self.days_until_due,
            'completion_time': self.completion_time
        }

class Category(db.Model):
    """任务分类模型"""
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    color = db.Column(db.String(7), default='#667eea')  # 十六进制颜色
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关联关系
    todos = db.relationship('Todo', backref='category_obj', lazy='dynamic')
    
    def __repr__(self):
        return f'<Category {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'color': self.color,
            'description': self.description,
            'todo_count': self.todos.count()
        }

class Tag(db.Model):
    """标签模型"""
    __tablename__ = 'tags'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True, nullable=False)
    color = db.Column(db.String(7), default='#6c757d')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Tag {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'color': self.color
        }

class TodoTag(db.Model):
    """Todo和Tag的多对多关系表"""
    __tablename__ = 'todo_tags'
    
    id = db.Column(db.Integer, primary_key=True)
    todo_id = db.Column(db.Integer, db.ForeignKey('todos.id'), nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'), nullable=False)
    
    # 关联关系
    todo = db.relationship('Todo', backref=db.backref('todo_tags', lazy='dynamic'))
    tag = db.relationship('Tag', backref=db.backref('todo_tags', lazy='dynamic'))
    
    __table_args__ = (db.UniqueConstraint('todo_id', 'tag_id', name='_todo_tag_uc'),)

class User(db.Model):
    """用户模型（为未来扩展准备）"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<User {self.username}>' 