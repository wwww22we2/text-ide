from typing import List, Dict, Any, Optional
from datetime import datetime
from models import db, Todo, Category, Tag, TodoTag
from utils import ValidationUtils, DataUtils, DateTimeUtils, ErrorHandler
import json
import logging

logger = logging.getLogger(__name__)

class TodoService:
    """Todo任务服务类"""
    
    @staticmethod
    def get_all_todos(filters: Dict[str, Any] = None, sort_by: str = 'priority', order: str = 'asc') -> List[Todo]:
        """获取所有任务"""
        try:
            query = Todo.query
            
            # 应用过滤器
            if filters:
                if 'completed' in filters:
                    query = query.filter(Todo.completed == filters['completed'])
                if 'priority' in filters:
                    query = query.filter(Todo.priority == filters['priority'])
                if 'category' in filters:
                    query = query.filter(Todo.category == filters['category'])
                if 'overdue' in filters and filters['overdue']:
                    query = query.filter(Todo.due_date < datetime.utcnow(), Todo.completed == False)
            
            # 应用排序
            if sort_by == 'priority':
                priority_order = {'high': 1, 'medium': 2, 'low': 3}
                query = query.order_by(Todo.completed.asc(), Todo.priority.asc(), Todo.created_at.asc())
            elif sort_by == 'created_at':
                query = query.order_by(Todo.created_at.desc() if order == 'desc' else Todo.created_at.asc())
            elif sort_by == 'due_date':
                query = query.order_by(Todo.due_date.asc() if order == 'asc' else Todo.due_date.desc())
            
            todos = query.all()
            return todos
        except Exception as e:
            logger.error(f"获取任务列表失败: {e}")
            raise
    
    @staticmethod
    def get_todo_by_id(todo_id: int) -> Optional[Todo]:
        """根据ID获取任务"""
        try:
            return Todo.query.get(todo_id)
        except Exception as e:
            logger.error(f"获取任务失败: {e}")
            raise
    
    @staticmethod
    def create_todo(data: Dict[str, Any]) -> Todo:
        """创建新任务"""
        try:
            # 验证数据
            content_validation = ValidationUtils.validate_todo_content(data.get('content', ''))
            if not content_validation['valid']:
                raise ValueError(content_validation['error'])
            
            priority_validation = ValidationUtils.validate_priority(data.get('priority', 'medium'))
            if not priority_validation['valid']:
                raise ValueError(priority_validation['error'])
            
            # 创建任务
            todo = Todo(
                content=content_validation['content'],
                priority=priority_validation['priority'],
                due_date=DateTimeUtils.parse_datetime(data.get('due_date')) if data.get('due_date') else None,
                notes=ValidationUtils.sanitize_input(data.get('notes', '')),
                category=data.get('category'),
                estimated_time=data.get('estimated_time'),
                tags=json.dumps(data.get('tags', [])) if data.get('tags') else None
            )
            
            db.session.add(todo)
            db.session.commit()
            
            logger.info(f"创建任务成功: {todo.id}")
            return todo
        except Exception as e:
            db.session.rollback()
            logger.error(f"创建任务失败: {e}")
            raise
    
    @staticmethod
    def update_todo(todo_id: int, data: Dict[str, Any]) -> Todo:
        """更新任务"""
        try:
            todo = TodoService.get_todo_by_id(todo_id)
            if not todo:
                raise ValueError("任务不存在")
            
            # 验证数据
            if 'content' in data:
                content_validation = ValidationUtils.validate_todo_content(data['content'])
                if not content_validation['valid']:
                    raise ValueError(content_validation['error'])
                todo.content = content_validation['content']
            
            if 'priority' in data:
                priority_validation = ValidationUtils.validate_priority(data['priority'])
                if not priority_validation['valid']:
                    raise ValueError(priority_validation['error'])
                todo.priority = priority_validation['priority']
            
            if 'due_date' in data:
                todo.due_date = DateTimeUtils.parse_datetime(data['due_date']) if data['due_date'] else None
            
            if 'notes' in data:
                todo.notes = ValidationUtils.sanitize_input(data['notes'])
            
            if 'category' in data:
                todo.category = data['category']
            
            if 'estimated_time' in data:
                todo.estimated_time = data['estimated_time']
            
            if 'tags' in data:
                todo.tags = json.dumps(data['tags']) if data['tags'] else None
            
            db.session.commit()
            
            logger.info(f"更新任务成功: {todo_id}")
            return todo
        except Exception as e:
            db.session.rollback()
            logger.error(f"更新任务失败: {e}")
            raise
    
    @staticmethod
    def delete_todo(todo_id: int) -> bool:
        """删除任务"""
        try:
            todo = TodoService.get_todo_by_id(todo_id)
            if not todo:
                raise ValueError("任务不存在")
            
            db.session.delete(todo)
            db.session.commit()
            
            logger.info(f"删除任务成功: {todo_id}")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"删除任务失败: {e}")
            raise
    
    @staticmethod
    def mark_completed(todo_id: int) -> Todo:
        """标记任务为完成"""
        try:
            todo = TodoService.get_todo_by_id(todo_id)
            if not todo:
                raise ValueError("任务不存在")
            
            todo.mark_completed()
            db.session.commit()
            
            logger.info(f"标记任务完成: {todo_id}")
            return todo
        except Exception as e:
            db.session.rollback()
            logger.error(f"标记任务完成失败: {e}")
            raise
    
    @staticmethod
    def mark_incomplete(todo_id: int) -> Todo:
        """标记任务为未完成"""
        try:
            todo = TodoService.get_todo_by_id(todo_id)
            if not todo:
                raise ValueError("任务不存在")
            
            todo.mark_incomplete()
            db.session.commit()
            
            logger.info(f"标记任务未完成: {todo_id}")
            return todo
        except Exception as e:
            db.session.rollback()
            logger.error(f"标记任务未完成失败: {e}")
            raise
    
    @staticmethod
    def get_stats() -> Dict[str, Any]:
        """获取统计信息"""
        try:
            todos = TodoService.get_all_todos()
            return DataUtils.calculate_stats(todos)
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            raise
    
    @staticmethod
    def bulk_update(todo_ids: List[int], updates: Dict[str, Any]) -> List[Todo]:
        """批量更新任务"""
        try:
            todos = []
            for todo_id in todo_ids:
                todo = TodoService.update_todo(todo_id, updates)
                todos.append(todo)
            
            logger.info(f"批量更新任务成功: {len(todo_ids)}个任务")
            return todos
        except Exception as e:
            logger.error(f"批量更新任务失败: {e}")
            raise
    
    @staticmethod
    def bulk_delete(todo_ids: List[int]) -> bool:
        """批量删除任务"""
        try:
            for todo_id in todo_ids:
                TodoService.delete_todo(todo_id)
            
            logger.info(f"批量删除任务成功: {len(todo_ids)}个任务")
            return True
        except Exception as e:
            logger.error(f"批量删除任务失败: {e}")
            raise

class CategoryService:
    """分类服务类"""
    
    @staticmethod
    def get_all_categories() -> List[Category]:
        """获取所有分类"""
        try:
            return Category.query.all()
        except Exception as e:
            logger.error(f"获取分类列表失败: {e}")
            raise
    
    @staticmethod
    def create_category(name: str, color: str = '#667eea', description: str = None) -> Category:
        """创建分类"""
        try:
            if not name or not name.strip():
                raise ValueError("分类名称不能为空")
            
            # 检查分类名是否已存在
            existing = Category.query.filter_by(name=name.strip()).first()
            if existing:
                raise ValueError("分类名称已存在")
            
            category = Category(
                name=name.strip(),
                color=color,
                description=description
            )
            
            db.session.add(category)
            db.session.commit()
            
            logger.info(f"创建分类成功: {category.id}")
            return category
        except Exception as e:
            db.session.rollback()
            logger.error(f"创建分类失败: {e}")
            raise
    
    @staticmethod
    def update_category(category_id: int, data: Dict[str, Any]) -> Category:
        """更新分类"""
        try:
            category = Category.query.get(category_id)
            if not category:
                raise ValueError("分类不存在")
            
            if 'name' in data:
                if not data['name'] or not data['name'].strip():
                    raise ValueError("分类名称不能为空")
                category.name = data['name'].strip()
            
            if 'color' in data:
                category.color = data['color']
            
            if 'description' in data:
                category.description = data['description']
            
            db.session.commit()
            
            logger.info(f"更新分类成功: {category_id}")
            return category
        except Exception as e:
            db.session.rollback()
            logger.error(f"更新分类失败: {e}")
            raise
    
    @staticmethod
    def delete_category(category_id: int) -> bool:
        """删除分类"""
        try:
            category = Category.query.get(category_id)
            if not category:
                raise ValueError("分类不存在")
            
            # 检查是否有任务使用此分类
            if category.todos.count() > 0:
                raise ValueError("无法删除正在使用的分类")
            
            db.session.delete(category)
            db.session.commit()
            
            logger.info(f"删除分类成功: {category_id}")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"删除分类失败: {e}")
            raise

class TagService:
    """标签服务类"""
    
    @staticmethod
    def get_all_tags() -> List[Tag]:
        """获取所有标签"""
        try:
            return Tag.query.all()
        except Exception as e:
            logger.error(f"获取标签列表失败: {e}")
            raise
    
    @staticmethod
    def create_tag(name: str, color: str = '#6c757d') -> Tag:
        """创建标签"""
        try:
            if not name or not name.strip():
                raise ValueError("标签名称不能为空")
            
            # 检查标签名是否已存在
            existing = Tag.query.filter_by(name=name.strip()).first()
            if existing:
                raise ValueError("标签名称已存在")
            
            tag = Tag(
                name=name.strip(),
                color=color
            )
            
            db.session.add(tag)
            db.session.commit()
            
            logger.info(f"创建标签成功: {tag.id}")
            return tag
        except Exception as e:
            db.session.rollback()
            logger.error(f"创建标签失败: {e}")
            raise
    
    @staticmethod
    def delete_tag(tag_id: int) -> bool:
        """删除标签"""
        try:
            tag = Tag.query.get(tag_id)
            if not tag:
                raise ValueError("标签不存在")
            
            # 检查是否有任务使用此标签
            if tag.todo_tags.count() > 0:
                raise ValueError("无法删除正在使用的标签")
            
            db.session.delete(tag)
            db.session.commit()
            
            logger.info(f"删除标签成功: {tag_id}")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"删除标签失败: {e}")
            raise 