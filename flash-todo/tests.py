#!/usr/bin/env python3
"""
Flash Todo 应用测试文件
"""

import unittest
import tempfile
import os
import json
from datetime import datetime, timedelta

from app_new import create_app
from models import db, Todo, Category, Tag
from services import TodoService, CategoryService, TagService
from utils import ValidationUtils, DateTimeUtils, DataUtils

class TodoTestCase(unittest.TestCase):
    """Todo应用测试用例"""
    
    def setUp(self):
        """测试前准备"""
        # 创建临时数据库
        self.db_fd, self.db_path = tempfile.mkstemp()
        
        # 创建测试应用
        self.app = create_app('testing')
        self.app.config['DATABASE'] = self.db_path
        self.app.config['TESTING'] = True
        
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
    
    def tearDown(self):
        """测试后清理"""
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def test_home_page(self):
        """测试主页"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Todo List', response.data)
    
    def test_create_todo(self):
        """测试创建任务"""
        with self.app.app_context():
            # 测试有效数据
            todo_data = {
                'content': '测试任务',
                'priority': 'medium',
                'category': '测试',
                'notes': '这是一个测试任务'
            }
            
            todo = TodoService.create_todo(todo_data)
            self.assertIsNotNone(todo)
            self.assertEqual(todo.content, '测试任务')
            self.assertEqual(todo.priority, 'medium')
            
            # 测试无效数据
            with self.assertRaises(ValueError):
                TodoService.create_todo({'content': ''})
    
    def test_update_todo(self):
        """测试更新任务"""
        with self.app.app_context():
            # 创建任务
            todo = TodoService.create_todo({
                'content': '原始任务',
                'priority': 'low'
            })
            
            # 更新任务
            updated_todo = TodoService.update_todo(todo.id, {
                'content': '更新后的任务',
                'priority': 'high'
            })
            
            self.assertEqual(updated_todo.content, '更新后的任务')
            self.assertEqual(updated_todo.priority, 'high')
    
    def test_delete_todo(self):
        """测试删除任务"""
        with self.app.app_context():
            # 创建任务
            todo = TodoService.create_todo({
                'content': '要删除的任务',
                'priority': 'medium'
            })
            
            # 删除任务
            result = TodoService.delete_todo(todo.id)
            self.assertTrue(result)
            
            # 验证任务已删除
            deleted_todo = TodoService.get_todo_by_id(todo.id)
            self.assertIsNone(deleted_todo)
    
    def test_mark_completed(self):
        """测试标记任务完成"""
        with self.app.app_context():
            # 创建任务
            todo = TodoService.create_todo({
                'content': '要完成的任务',
                'priority': 'medium'
            })
            
            # 标记完成
            completed_todo = TodoService.mark_completed(todo.id)
            self.assertTrue(completed_todo.completed)
            self.assertIsNotNone(completed_todo.completed_at)
    
    def test_get_stats(self):
        """测试获取统计信息"""
        with self.app.app_context():
            # 创建一些任务
            TodoService.create_todo({'content': '任务1', 'priority': 'high'})
            TodoService.create_todo({'content': '任务2', 'priority': 'medium'})
            TodoService.create_todo({'content': '任务3', 'priority': 'low'})
            
            # 标记一个任务完成
            todos = TodoService.get_all_todos()
            TodoService.mark_completed(todos[0].id)
            
            # 获取统计信息
            stats = TodoService.get_stats()
            self.assertEqual(stats['total'], 3)
            self.assertEqual(stats['completed'], 1)
            self.assertEqual(stats['pending'], 2)
            self.assertEqual(stats['completion_rate'], 33.3)
    
    def test_api_endpoints(self):
        """测试API端点"""
        # 测试获取任务列表API
        response = self.client.get('/api/todos')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        
        # 测试创建任务API
        todo_data = {
            'content': 'API测试任务',
            'priority': 'medium'
        }
        response = self.client.post('/api/todos',
                                  data=json.dumps(todo_data),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 201)
        
        # 测试获取统计信息API
        response = self.client.get('/api/stats')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('total', data)
        self.assertIn('completed', data)
        self.assertIn('pending', data)
    
    def test_validation_utils(self):
        """测试验证工具"""
        # 测试任务内容验证
        result = ValidationUtils.validate_todo_content('有效内容')
        self.assertTrue(result['valid'])
        
        result = ValidationUtils.validate_todo_content('')
        self.assertFalse(result['valid'])
        
        # 测试优先级验证
        result = ValidationUtils.validate_priority('high')
        self.assertTrue(result['valid'])
        
        result = ValidationUtils.validate_priority('invalid')
        self.assertFalse(result['valid'])
    
    def test_datetime_utils(self):
        """测试日期时间工具"""
        # 测试日期格式化
        dt = datetime.now()
        formatted = DateTimeUtils.format_datetime(dt)
        self.assertIsNotNone(formatted)
        
        # 测试相对时间
        relative = DateTimeUtils.get_relative_time(dt)
        self.assertIsNotNone(relative)
        
        # 测试日期解析
        parsed = DateTimeUtils.parse_datetime('2023-12-01')
        self.assertIsNotNone(parsed)
        
        # 测试无效日期
        parsed = DateTimeUtils.parse_datetime('invalid-date')
        self.assertIsNone(parsed)
    
    def test_data_utils(self):
        """测试数据处理工具"""
        with self.app.app_context():
            # 创建测试数据
            todos = []
            for i in range(5):
                todo = TodoService.create_todo({
                    'content': f'任务{i}',
                    'priority': 'medium' if i % 2 == 0 else 'high'
                })
                todos.append(todo)
            
            # 测试统计计算
            stats = DataUtils.calculate_stats(todos)
            self.assertEqual(stats['total'], 5)
            self.assertEqual(stats['pending'], 5)
            
            # 测试排序
            sorted_todos = DataUtils.sort_todos(todos, 'priority', 'asc')
            self.assertEqual(len(sorted_todos), 5)
            
            # 测试过滤
            filtered_todos = DataUtils.filter_todos(todos, {'priority': 'high'})
            self.assertLess(len(filtered_todos), 5)
    
    def test_category_service(self):
        """测试分类服务"""
        with self.app.app_context():
            # 创建分类
            category = CategoryService.create_category(
                name='测试分类',
                color='#ff0000',
                description='测试分类描述'
            )
            self.assertIsNotNone(category)
            self.assertEqual(category.name, '测试分类')
            
            # 获取所有分类
            categories = CategoryService.get_all_categories()
            self.assertGreater(len(categories), 0)
            
            # 更新分类
            updated_category = CategoryService.update_category(
                category.id,
                {'name': '更新后的分类'}
            )
            self.assertEqual(updated_category.name, '更新后的分类')
    
    def test_tag_service(self):
        """测试标签服务"""
        with self.app.app_context():
            # 创建标签
            tag = TagService.create_tag(
                name='测试标签',
                color='#00ff00'
            )
            self.assertIsNotNone(tag)
            self.assertEqual(tag.name, '测试标签')
            
            # 获取所有标签
            tags = TagService.get_all_tags()
            self.assertGreater(len(tags), 0)
    
    def test_error_handling(self):
        """测试错误处理"""
        # 测试404错误
        response = self.client.get('/nonexistent')
        self.assertEqual(response.status_code, 302)  # 重定向到首页
        
        # 测试API 404错误
        response = self.client.get('/api/nonexistent')
        self.assertEqual(response.status_code, 404)
    
    def test_form_validation(self):
        """测试表单验证"""
        # 测试空内容
        response = self.client.post('/', data={
            'content': '',
            'priority': 'medium'
        }, follow_redirects=True)
        self.assertIn(b'Task content cannot be empty', response.data)
        
        # 测试有效内容
        response = self.client.post('/', data={
            'content': 'Valid task content',
            'priority': 'high'
        }, follow_redirects=True)
        self.assertIn(b'Task added successfully', response.data)

def run_tests():
    """运行测试"""
    # 创建测试套件
    suite = unittest.TestLoader().loadTestsFromTestCase(TodoTestCase)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 返回测试结果
    return result.wasSuccessful()

if __name__ == '__main__':
    # 运行所有测试
    success = run_tests()
    
    # 根据测试结果退出
    sys.exit(0 if success else 1) 