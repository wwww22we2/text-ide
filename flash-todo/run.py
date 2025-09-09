#!/usr/bin/env python3
"""
Flash Todo 应用启动脚本
"""

import os
import sys
import argparse
from app_new import create_app

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Flash Todo 应用启动脚本')
    parser.add_argument('--env', choices=['development', 'production', 'testing'], 
                       default='development', help='运行环境')
    parser.add_argument('--host', default='0.0.0.0', help='监听地址')
    parser.add_argument('--port', type=int, default=5000, help='监听端口')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    parser.add_argument('--init-db', action='store_true', help='初始化数据库')
    parser.add_argument('--sample-data', action='store_true', help='创建示例数据')
    
    args = parser.parse_args()
    
    # 设置环境变量
    os.environ['FLASK_ENV'] = args.env
    
    # 创建应用
    app = create_app(args.env)
    
    # 初始化数据库
    if args.init_db:
        print("🗄️  初始化数据库...")
        with app.app_context():
            from migrations import init_database
            init_database()
    
    # 创建示例数据
    if args.sample_data:
        print("📝 创建示例数据...")
        with app.app_context():
            from migrations import create_sample_data
            create_sample_data()
    
    # 启动应用
    print(f"🚀 Flash Todo 应用启动中...")
    print(f"📱 环境: {args.env}")
    print(f"🌐 地址: http://{args.host}:{args.port}")
    print(f"🔧 调试: {'开启' if args.debug else '关闭'}")
    print(f"💡 按 Ctrl+C 停止服务器")
    
    app.run(
        host=args.host,
        port=args.port,
        debug=args.debug
    )

if __name__ == "__main__":
    main() 