import json
import re
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from flask import current_app
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DateTimeUtils:
    """日期时间工具类"""
    
    @staticmethod
    def format_datetime(dt: datetime) -> str:
        """格式化日期时间为可读格式"""
        if not dt:
            return None
        try:
            return dt.strftime('%Y年%m月%d日 %H:%M')
        except Exception as e:
            logger.error(f"格式化日期时间失败: {e}")
            return str(dt)
    
    @staticmethod
    def get_relative_time(dt: datetime) -> str:
        """获取相对时间(如:2小时前)"""
        if not dt:
            return None
        try:
            now = datetime.utcnow()
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
        except Exception as e:
            logger.error(f"计算相对时间失败: {e}")
            return None
    
    @staticmethod
    def parse_datetime(date_str: str) -> Optional[datetime]:
        """解析日期时间字符串"""
        if not date_str:
            return None
        
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M',
            '%Y-%m-%d',
            '%Y/%m/%d %H:%M:%S',
            '%Y/%m/%d %H:%M',
            '%Y/%m/%d'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        return None
    
    @staticmethod
    def is_valid_date(date_str: str) -> bool:
        """验证日期字符串是否有效"""
        return DateTimeUtils.parse_datetime(date_str) is not None

class ValidationUtils:
    """数据验证工具类"""
    
    @staticmethod
    def validate_todo_content(content: str) -> Dict[str, Any]:
        """验证任务内容"""
        if not content or not content.strip():
            return {'valid': False, 'error': '任务内容不能为空'}
        
        content = content.strip()
        if len(content) > 500:
            return {'valid': False, 'error': '任务内容不能超过500个字符'}
        
        if len(content) < 2:
            return {'valid': False, 'error': '任务内容至少需要2个字符'}
        
        return {'valid': True, 'content': content}
    
    @staticmethod
    def validate_priority(priority: str) -> Dict[str, Any]:
        """验证优先级"""
        valid_priorities = ['low', 'medium', 'high']
        if priority not in valid_priorities:
            return {'valid': False, 'error': '无效的优先级值'}
        
        return {'valid': True, 'priority': priority}
    
    @staticmethod
    def validate_tags(tags_str: str) -> Dict[str, Any]:
        """验证标签字符串"""
        if not tags_str:
            return {'valid': True, 'tags': []}
        
        try:
            tags = json.loads(tags_str) if isinstance(tags_str, str) else tags_str
            if not isinstance(tags, list):
                return {'valid': False, 'error': '标签格式错误'}
            
            # 验证每个标签
            valid_tags = []
            for tag in tags:
                if isinstance(tag, str) and 1 <= len(tag) <= 20:
                    valid_tags.append(tag.strip())
                else:
                    return {'valid': False, 'error': f'无效的标签: {tag}'}
            
            return {'valid': True, 'tags': valid_tags}
        except json.JSONDecodeError:
            return {'valid': False, 'error': '标签JSON格式错误'}
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """清理用户输入"""
        if not text:
            return ""
        
        # 移除潜在的XSS攻击代码
        text = re.sub(r'<script.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'<.*?>', '', text)  # 移除所有HTML标签
        
        # 限制长度
        if len(text) > 1000:
            text = text[:1000]
        
        return text.strip()

class DataUtils:
    """数据处理工具类"""
    
    @staticmethod
    def calculate_stats(todos: List) -> Dict[str, Any]:
        """计算任务统计信息"""
        total = len(todos)
        completed = sum(1 for todo in todos if todo.completed)
        pending = total - completed
        completion_rate = round((completed / total * 100) if total > 0 else 0, 1)
        
        # 按优先级统计
        priority_stats = {
            'high': sum(1 for todo in todos if todo.priority == 'high'),
            'medium': sum(1 for todo in todos if todo.priority == 'medium'),
            'low': sum(1 for todo in todos if todo.priority == 'low')
        }
        
        # 逾期任务统计
        overdue = sum(1 for todo in todos if hasattr(todo, 'is_overdue') and todo.is_overdue)
        
        # 今日任务统计
        today = datetime.utcnow().date()
        today_todos = sum(1 for todo in todos if todo.created_at and todo.created_at.date() == today)
        
        return {
            'total': total,
            'completed': completed,
            'pending': pending,
            'completion_rate': completion_rate,
            'priority_stats': priority_stats,
            'overdue': overdue,
            'today_todos': today_todos
        }
    
    @staticmethod
    def sort_todos(todos: List, sort_by: str = 'priority', order: str = 'asc') -> List:
        """排序任务列表"""
        reverse = order.lower() == 'desc'
        
        if sort_by == 'priority':
            priority_order = {'high': 1, 'medium': 2, 'low': 3}
            return sorted(todos, key=lambda x: priority_order.get(x.priority, 2), reverse=reverse)
        elif sort_by == 'created_at':
            return sorted(todos, key=lambda x: x.created_at or datetime.min, reverse=reverse)
        elif sort_by == 'due_date':
            return sorted(todos, key=lambda x: x.due_date or datetime.max, reverse=reverse)
        elif sort_by == 'completed':
            return sorted(todos, key=lambda x: x.completed, reverse=reverse)
        else:
            return todos
    
    @staticmethod
    def filter_todos(todos: List, filters: Dict[str, Any]) -> List:
        """过滤任务列表"""
        filtered_todos = todos
        
        # 按完成状态过滤
        if 'completed' in filters:
            filtered_todos = [t for t in filtered_todos if t.completed == filters['completed']]
        
        # 按优先级过滤
        if 'priority' in filters:
            filtered_todos = [t for t in filtered_todos if t.priority == filters['priority']]
        
        # 按分类过滤
        if 'category' in filters:
            filtered_todos = [t for t in filtered_todos if t.category == filters['category']]
        
        # 按标签过滤
        if 'tags' in filters:
            for tag in filters['tags']:
                filtered_todos = [t for t in filtered_todos if t.tags and tag in json.loads(t.tags)]
        
        # 按日期范围过滤
        if 'date_from' in filters:
            date_from = DateTimeUtils.parse_datetime(filters['date_from'])
            if date_from:
                filtered_todos = [t for t in filtered_todos if t.created_at and t.created_at >= date_from]
        
        if 'date_to' in filters:
            date_to = DateTimeUtils.parse_datetime(filters['date_to'])
            if date_to:
                filtered_todos = [t for t in filtered_todos if t.created_at and t.created_at <= date_to]
        
        return filtered_todos

class ErrorHandler:
    """错误处理工具类"""
    
    @staticmethod
    def handle_database_error(e: Exception) -> str:
        """处理数据库错误"""
        logger.error(f"数据库错误: {e}")
        return "数据库操作失败，请稍后重试"
    
    @staticmethod
    def handle_validation_error(e: Exception) -> str:
        """处理验证错误"""
        logger.error(f"验证错误: {e}")
        return "数据验证失败，请检查输入"
    
    @staticmethod
    def handle_general_error(e: Exception) -> str:
        """处理一般错误"""
        logger.error(f"一般错误: {e}")
        return "操作失败，请稍后重试"

class CacheUtils:
    """缓存工具类"""
    
    @staticmethod
    def get_cache_key(prefix: str, *args) -> str:
        """生成缓存键"""
        return f"{prefix}:{':'.join(str(arg) for arg in args)}"
    
    @staticmethod
    def cache_result(func):
        """缓存装饰器"""
        def wrapper(*args, **kwargs):
            # 这里可以实现缓存逻辑
            # 目前简单返回原函数结果
            return func(*args, **kwargs)
        return wrapper

# 全局工具函数
def format_datetime(datetime_str):
    """格式化时间字符串为可读格式（兼容旧版本）"""
    if not datetime_str:
        return None
    try:
        dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        return DateTimeUtils.format_datetime(dt)
    except:
        return datetime_str

def get_relative_time(datetime_str):
    """获取相对时间(如:2小时前)（兼容旧版本）"""
    if not datetime_str:
        return None
    try:
        dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        return DateTimeUtils.get_relative_time(dt)      
            
    except:
        return None 

