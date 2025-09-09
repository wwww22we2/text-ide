import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler

from config import config
from models import db
from services import TodoService, CategoryService, TagService
from utils import DateTimeUtils, ValidationUtils, ErrorHandler

def create_app(config_name='development'):
    """应用工厂函数"""
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object(config[config_name])
    
    # 初始化扩展
    db.init_app(app)
    migrate = Migrate(app, db)
    CORS(app)
    
    # 初始化限流器
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"]
    )
    
    # 配置日志
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/todo_app.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Todo应用启动')
    
    # 注册模板过滤器
    app.jinja_env.filters['format_datetime'] = DateTimeUtils.format_datetime
    app.jinja_env.filters['relative_time'] = DateTimeUtils.get_relative_time
    
    # 注册路由
    register_routes(app)
    
    # 注册错误处理器
    register_error_handlers(app)
    
    return app

def register_routes(app):
    """注册路由"""
    
    @app.route("/", methods=["GET", "POST"])
    @limiter.limit("10 per minute")
    def index():
        """主页 - 显示任务列表"""
        if request.method == "POST":
            try:
                # 获取表单数据
                content = request.form.get("content", "").strip()
                priority = request.form.get("priority", "medium")
                due_date = request.form.get("due_date", "")
                category = request.form.get("category", "")
                notes = request.form.get("notes", "")
                tags = request.form.get("tags", "")
                
                # 创建任务数据
                todo_data = {
                    'content': content,
                    'priority': priority,
                    'due_date': due_date if due_date else None,
                    'category': category if category else None,
                    'notes': notes,
                    'tags': [tag.strip() for tag in tags.split(',') if tag.strip()] if tags else []
                }
                
                # 创建任务
                TodoService.create_todo(todo_data)
                flash("任务添加成功！", "success")
                
            except ValueError as e:
                flash(str(e), "error")
            except Exception as e:
                flash(ErrorHandler.handle_general_error(e), "error")
            
            return redirect(url_for("index"))
        
        try:
            # 获取过滤和排序参数
            filters = {}
            if request.args.get('completed') == 'true':
                filters['completed'] = True
            elif request.args.get('completed') == 'false':
                filters['completed'] = False
            
            if request.args.get('priority'):
                filters['priority'] = request.args.get('priority')
            
            if request.args.get('category'):
                filters['category'] = request.args.get('category')
            
            if request.args.get('overdue') == 'true':
                filters['overdue'] = True
            
            sort_by = request.args.get('sort_by', 'priority')
            order = request.args.get('order', 'asc')
            
            # 获取任务列表
            todos = TodoService.get_all_todos(filters, sort_by, order)
            
            # 获取分类列表
            categories = CategoryService.get_all_categories()
            
            # 获取标签列表
            tags = TagService.get_all_tags()
            
            return render_template("index.html", 
                                 todos=todos, 
                                 categories=categories, 
                                 tags=tags,
                                 filters=filters,
                                 sort_by=sort_by,
                                 order=order)
        
        except Exception as e:
            flash(ErrorHandler.handle_general_error(e), "error")
            return render_template("index.html", todos=[], categories=[], tags=[])
    
    @app.route("/todo/<int:todo_id>")
    def todo_detail(todo_id):
        """任务详情页面"""
        try:
            todo = TodoService.get_todo_by_id(todo_id)
            if not todo:
                abort(404)
            
            categories = CategoryService.get_all_categories()
            tags = TagService.get_all_tags()
            
            return render_template("todo_detail.html", 
                                 todo=todo, 
                                 categories=categories, 
                                 tags=tags)
        
        except Exception as e:
            flash(ErrorHandler.handle_general_error(e), "error")
            return redirect(url_for("index"))
    
    @app.route("/edit/<int:todo_id>", methods=["GET", "POST"])
    def edit_todo(todo_id):
        """编辑任务"""
        try:
            todo = TodoService.get_todo_by_id(todo_id)
            if not todo:
                flash("任务不存在！", "error")
                return redirect(url_for("index"))
            
            if request.method == "POST":
                # 获取表单数据
                content = request.form.get("content", "").strip()
                priority = request.form.get("priority", "medium")
                due_date = request.form.get("due_date", "")
                category = request.form.get("category", "")
                notes = request.form.get("notes", "")
                tags = request.form.get("tags", "")
                
                # 更新任务数据
                todo_data = {
                    'content': content,
                    'priority': priority,
                    'due_date': due_date if due_date else None,
                    'category': category if category else None,
                    'notes': notes,
                    
                    'tags': [tag.strip() for tag in tags.split(',') if tag.strip()] if tags else []
                }
                
                # 更新任务
                TodoService.update_todo(todo_id, todo_data)
                flash("任务更新成功！", "success")
                return redirect(url_for("index"))
            
            categories = CategoryService.get_all_categories()
            tags = TagService.get_all_tags()
            
            return render_template("edit.html", 
                                 todo=todo, 
                                 categories=categories, 
                                 tags=tags)
        
        except ValueError as e:
            flash(str(e), "error")
        except Exception as e:
            flash(ErrorHandler.handle_general_error(e), "error")
        
        return redirect(url_for("index"))
    
    @app.route("/complete/<int:todo_id>")
    def complete_todo(todo_id):
        """标记任务为完成"""
        try:
            TodoService.mark_completed(todo_id)
            flash("任务已标记为完成！", "success")
        except Exception as e:
            flash(ErrorHandler.handle_general_error(e), "error")
        
        return redirect(url_for("index"))
    
    @app.route("/uncomplete/<int:todo_id>")
    def uncomplete_todo(todo_id):
        """标记任务为未完成"""
        try:
            TodoService.mark_incomplete(todo_id)
            flash("任务已标记为未完成！", "info")
        except Exception as e:
            flash(ErrorHandler.handle_general_error(e), "error")
        
        return redirect(url_for("index"))
    
    @app.route("/delete/<int:todo_id>")
    def delete_todo(todo_id):
        """删除任务"""
        try:
            TodoService.delete_todo(todo_id)
            flash("任务已删除！", "info")
        except Exception as e:
            flash(ErrorHandler.handle_general_error(e), "error")
        
        return redirect(url_for("index"))
    
    # API路由
    @app.route("/api/todos", methods=["GET"])
    def api_get_todos():
        """API: 获取任务列表"""
        try:
            filters = {}
            if request.args.get('completed') == 'true':
                filters['completed'] = True
            elif request.args.get('completed') == 'false':
                filters['completed'] = False
            
            if request.args.get('priority'):
                filters['priority'] = request.args.get('priority')
            
            if request.args.get('category'):
                filters['category'] = request.args.get('category')
            
            sort_by = request.args.get('sort_by', 'priority')
            order = request.args.get('order', 'asc')
            
            todos = TodoService.get_all_todos(filters, sort_by, order)
            return jsonify([todo.to_dict() for todo in todos])
        
        except Exception as e:
            return jsonify({'error': ErrorHandler.handle_general_error(e)}), 500
    
    @app.route("/api/todos", methods=["POST"])
    def api_create_todo():
        """API: 创建任务"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': '无效的请求数据'}), 400
            
            todo = TodoService.create_todo(data)
            return jsonify(todo.to_dict()), 201
        
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': ErrorHandler.handle_general_error(e)}), 500
    
    @app.route("/api/todos/<int:todo_id>", methods=["GET"])
    def api_get_todo(todo_id):
        """API: 获取单个任务"""
        try:
            todo = TodoService.get_todo_by_id(todo_id)
            if not todo:
                return jsonify({'error': '任务不存在'}), 404
            
            return jsonify(todo.to_dict())
        
        except Exception as e:
            return jsonify({'error': ErrorHandler.handle_general_error(e)}), 500
    
    @app.route("/api/todos/<int:todo_id>", methods=["PUT"])
    def api_update_todo(todo_id):
        """API: 更新任务"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': '无效的请求数据'}), 400
            
            todo = TodoService.update_todo(todo_id, data)
            return jsonify(todo.to_dict())
        
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': ErrorHandler.handle_general_error(e)}), 500
    
    @app.route("/api/todos/<int:todo_id>", methods=["DELETE"])
    def api_delete_todo(todo_id):
        """API: 删除任务"""
        try:
            TodoService.delete_todo(todo_id)
            return jsonify({'message': '任务删除成功'})
        
        except Exception as e:
            return jsonify({'error': ErrorHandler.handle_general_error(e)}), 500
    
    @app.route("/api/stats")
    def api_stats():
        """API: 获取统计信息"""
        try:
            stats = TodoService.get_stats()
            return jsonify(stats)
        
        except Exception as e:
            return jsonify({'error': ErrorHandler.handle_general_error(e)}), 500
    
    @app.route("/api/categories", methods=["GET"])
    def api_get_categories():
        """API: 获取分类列表"""
        try:
            categories = CategoryService.get_all_categories()
            return jsonify([category.to_dict() for category in categories])
        
        except Exception as e:
            return jsonify({'error': ErrorHandler.handle_general_error(e)}), 500
    
    @app.route("/api/categories", methods=["POST"])
    def api_create_category():
        """API: 创建分类"""
        try:
            data = request.get_json()
            if not data or not data.get('name'):
                return jsonify({'error': '分类名称不能为空'}), 400
            
            category = CategoryService.create_category(
                name=data['name'],
                color=data.get('color', '#667eea'),
                description=data.get('description')
            )
            return jsonify(category.to_dict()), 201
        
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': ErrorHandler.handle_general_error(e)}), 500
    
    @app.route("/api/tags", methods=["GET"])
    def api_get_tags():
        """API: 获取标签列表"""
        try:
            tags = TagService.get_all_tags()
            return jsonify([tag.to_dict() for tag in tags])
        
        except Exception as e:
            return jsonify({'error': ErrorHandler.handle_general_error(e)}), 500
    
    @app.route("/api/tags", methods=["POST"])
    def api_create_tag():
        """API: 创建标签"""
        try:
            data = request.get_json()
            if not data or not data.get('name'):
                return jsonify({'error': '标签名称不能为空'}), 400
            
            tag = TagService.create_tag(
                name=data['name'],
                color=data.get('color', '#6c757d')
            )
            return jsonify(tag.to_dict()), 201
        
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': ErrorHandler.handle_general_error(e)}), 500

def register_error_handlers(app):
    """注册错误处理器"""
    
    @app.errorhandler(404)
    def not_found_error(error):
        if request.path.startswith('/api/'):
            return jsonify({'error': '请求的资源不存在'}), 404
        flash("请求的页面不存在！", "error")
        return redirect(url_for("index"))
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        if request.path.startswith('/api/'):
            return jsonify({'error': '服务器内部错误'}), 500
        flash("服务器内部错误，请稍后重试！", "error")
        return redirect(url_for("index"))
    
    @app.errorhandler(413)
    def too_large(error):
        if request.path.startswith('/api/'):
            return jsonify({'error': '请求数据过大'}), 413
        flash("请求数据过大！", "error")
        return redirect(url_for("index"))
        

# 全局变量
limiter = None

if __name__ == "__main__":
    app = create_app()
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"]
    )
    
    print("🚀 Flask Todo 应用启动中...")
    print("📱 访问地址: http://localhost:5000")
    print("💡 按 Ctrl+C 停止服务器")
    
    app.run(debug=True, host='0.0.0.0', port=5000) 