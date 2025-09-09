#!/usr/bin/env python3
"""
数据库迁移脚本
用于初始化数据库和升级数据库结构
"""

import os
import sys
from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, upgrade, init, migrate

# 添加项目根目录到Python路径    确保可以导入项目的其他模块

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))      
# 从项目根目录导入配置和模型
from config import config
from models import db, Todo, Category, Tag, TodoTag, User

def create_migration_app():
    """创建用于迁移的Flask应用"""
    app = Flask(__name__)
    app.config.from_object(config['development'])
    db.init_app(app)
    return app

def init_database():
    """初始化数据库"""
    app = create_migration_app()
    
    with app.app_context():
        print("🗄️  初始化数据库...")
        
        # 创建所有表
        db.create_all()
        
        # 创建默认分类
        default_categories = [
            {'name': '工作', 'color': '#ff6b6b', 'description': '工作相关任务'},
            {'name': '学习', 'color': '#4ecdc4', 'description': '学习相关任务'},
            {'name': '生活', 'color': '#45b7d1', 'description': '日常生活任务'},
            {'name': '健康', 'color': '#96ceb4', 'description': '健康相关任务'},
            {'name': '娱乐', 'color': '#feca57', 'description': '娱乐休闲任务'}
        ]
        
        for cat_data in default_categories:
            
            existing = Category.query.filter_by(name=cat_data['name']).first()
            if not existing:
                category = Category(**cat_data)
                db.session.add(category)
                print(f"✅ 创建默认分类: {cat_data['name']}")
        
        # 创建默认标签
        default_tags = [
            {'name': '紧急', 'color': '#ff4757'},
            {'name': '重要', 'color': '#ffa502'},
            {'name': '日常', 'color': '#2ed573'},
            {'name': '项目', 'color': '#3742fa'},
            {'name': '会议', 'color': '#ff6348'}
        ]
        
        for tag_data in default_tags:
            existing = Tag.query.filter_by(name=tag_data['name']).first()
            if not existing:
                tag = Tag(**tag_data)
                db.session.add(tag)
                print(f"✅ 创建默认标签: {tag_data['name']}")
        
        # 提交更改
        db.session.commit()
        
        print("✅ 数据库初始化完成！")

def migrate_database():
    """执行数据库迁移"""
    app = create_migration_app()
    
    with app.app_context():
        print("🔄 执行数据库迁移...")
        
        try:
            # 初始化迁移
            init()
            print("✅ 迁移初始化完成")
        except Exception as e:
            print(f"⚠️  迁移可能已经初始化: {e}")
        
        try:
            # 创建迁移
            migrate()
            print("✅ 迁移文件创建完成")
        except Exception as e:
            print(f"⚠️  创建迁移失败: {e}")
        
        try:
            # 应用迁移
            upgrade()
            print("✅ 迁移应用完成")
        except Exception as e:
            print(f"⚠️  应用迁移失败: {e}")

def backup_database():
    """备份数据库"""
    import shutil
    from datetime import datetime
    
    backup_dir = 'backups'
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(backup_dir, f'todo_backup_{timestamp}.db')
    
    if os.path.exists('todo.db'):
        shutil.copy2('todo.db', backup_file)
        print(f"✅ 数据库备份完成: {backup_file}")
    else:
        print("⚠️  数据库文件不存在，跳过备份")

def restore_database(backup_file):
    """恢复数据库"""
    import shutil
    
    if not os.path.exists(backup_file):
        print(f"❌ 备份文件不存在: {backup_file}")
        return
    
    # 先备份当前数据库
    if os.path.exists('todo.db'):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        current_backup = f'todo_current_{timestamp}.db'
        shutil.copy2('todo.db', current_backup)
        print(f"✅ 当前数据库已备份: {current_backup}")
    
    # 恢复数据库
    shutil.copy2(backup_file, 'todo.db')
    print(f"✅ 数据库恢复完成: {backup_file}")

def show_database_info():
    """显示数据库信息"""
    app = create_migration_app()
    
    with app.app_context():
        print("📊 数据库信息:")
        print(f"  任务总数: {Todo.query.count()}")
        print(f"  分类总数: {Category.query.count()}")
        print(f"  标签总数: {Tag.query.count()}")
        print(f"  用户总数: {User.query.count()}")
        
        # 显示分类信息
        print("\n📁 分类信息:")
        categories = Category.query.all()
        for cat in categories:
            todo_count = Todo.query.filter_by(category=cat.name).count()
            print(f"  {cat.name}: {todo_count} 个任务")
        
        # 显示标签信息
        print("\n🏷️  标签信息:")
        tags = Tag.query.all()
        for tag in tags:
            todo_count = TodoTag.query.filter_by(tag_id=tag.id).count()
            print(f"  {tag.name}: {todo_count} 个任务")

def clear_database():
    """清空数据库"""
    app = create_migration_app()
    
    with app.app_context():
        print("🗑️  清空数据库...")
        
        # 删除所有数据
        TodoTag.query.delete()
        Todo.query.delete()
        Tag.query.delete()
        Category.query.delete()
        User.query.delete()
        
        db.session.commit()
        print("✅ 数据库已清空")

def create_sample_data():
    """创建示例数据"""
    app = create_migration_app()
    
    with app.app_context():
        print("📝 创建示例数据...")
        
        # 创建示例任务
        sample_todos = [
            {
                'content': '完成项目文档编写',
                'priority': 'high',
                'category': '工作',
                'notes': '需要在下周前完成项目文档的编写和审核',
                'tags': ['重要', '项目']
            },
            {
                'content': '学习Python Flask框架',
                'priority': 'medium',
                'category': '学习',
                'notes': '深入学习Flask框架的高级特性',
                'tags': ['学习', '技术']
            },
            {
                'content': '购买生日礼物',
                'priority': 'medium',
                'category': '生活',
                'notes': '为朋友准备生日礼物',
                'tags': ['日常']
            },
            {
                'content': '跑步30分钟',
                'priority': 'low',
                'category': '健康',
                'notes': '保持身体健康，每天运动',
                'tags': ['健康', '日常']
            },
            {
                'content': '看电影放松',
                'priority': 'low',
                'category': '娱乐',
                'notes': '周末看一部好电影放松心情',
                'tags': ['娱乐']
            }
        ]
        
        for todo_data in sample_todos:
            todo = Todo(
                content=todo_data['content'],
                priority=todo_data['priority'],
                category=todo_data['category'],
                notes=todo_data['notes'],
                tags=','.join(todo_data['tags'])
            )
            db.session.add(todo)
            print(f"✅ 创建示例任务: {todo_data['content']}")
        
        db.session.commit()
        print("✅ 示例数据创建完成！")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python migrations.py init      # 初始化数据库")
        print("  python migrations.py migrate   # 执行迁移")
        print("  python migrations.py backup    # 备份数据库")
        print("  python migrations.py restore <file>  # 恢复数据库")
        print("  python migrations.py info      # 显示数据库信息")
        print("  python migrations.py clear     # 清空数据库")
        print("  python migrations.py sample    # 创建示例数据")
        return
    
    command = sys.argv[1]
    
    if command == 'init':
        init_database()
    elif command == 'migrate':
        migrate_database()
    elif command == 'backup':
        backup_database()
    elif command == 'restore':
        if len(sys.argv) < 3:
            print("❌ 请指定备份文件路径")
            return
        restore_database(sys.argv[2])
    elif command == 'info':
        show_database_info()
    elif command == 'clear':
        confirm = input("⚠️  确定要清空数据库吗？(y/N): ")
        if confirm.lower() == 'y':
            clear_database()
        else:
            print("❌ 操作已取消")
    elif command == 'sample':
        create_sample_data()
    else:
        print(f"❌ 未知命令: {command}")

if __name__ == "__main__":
    main() 