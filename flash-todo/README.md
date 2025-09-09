# 🚀 Flash Todo - 现代化任务管理应用

一个功能完善、可扩展的Flask任务管理应用，支持任务分类、标签、优先级管理等功能。

## ✨ 主要特性

### 🎯 核心功能
- ✅ 任务创建、编辑、删除、完成/取消完成
- 🏷️ 任务分类和标签管理
- ⚡ 优先级设置（高、中、低）
- 📅 截止日期设置和逾期提醒
- 📝 任务备注和详细描述
- 🔍 高级搜索和过滤功能
- 📊 实时统计和进度跟踪

### 🛠️ 技术特性
- 🏗️ 模块化架构设计
- 🔒 完善的安全机制
- 📈 性能优化和缓存
- 🐳 Docker容器化部署
- 📱 响应式设计
- 🔌 RESTful API接口
- 📋 完整的错误处理
- 📝 详细的日志记录

### 🚀 部署特性
- 🐳 Docker & Docker Compose支持
- 🌐 Nginx反向代理
- 🔄 自动备份机制
- 📊 健康检查
- 🔧 环境配置管理

## 🛠️ 技术栈

### 后端
- **Flask 3.0** - Web框架
- **SQLAlchemy** - ORM数据库操作
- **Flask-Migrate** - 数据库迁移
- **Flask-CORS** - 跨域支持
- **Flask-Limiter** - 请求限流
- **Gunicorn** - WSGI服务器

### 前端
- **HTML5/CSS3** - 现代化UI设计
- **JavaScript** - 交互功能
- **Font Awesome** - 图标库
- **响应式设计** - 移动端适配

### 数据库
- **SQLite** - 开发环境
- **PostgreSQL** - 生产环境（可选）

### 部署
- **Docker** - 容器化
- **Nginx** - 反向代理
- **Redis** - 缓存和会话存储

## 📦 安装和运行

### 1. 环境要求
- Python 3.8+
- pip
- Git

### 2. 克隆项目
```bash
git clone <repository-url>
cd flash-todo
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 环境配置
```bash
# 复制环境变量示例文件
cp env_example.txt .env

# 编辑环境变量
nano .env
```

### 5. 初始化数据库
```bash
# 初始化数据库
python migrations.py init

# 创建示例数据（可选）
python migrations.py sample
```

### 6. 运行应用
```bash
# 开发环境
python app_new.py

# 或者使用Flask命令
export FLASK_APP=app_new.py
export FLASK_ENV=development
flask run
```

访问 http://localhost:5000 查看应用

## 🐳 Docker部署

### 1. 构建镜像
```bash
docker build -t flash-todo .
```

### 2. 运行容器
```bash
# 使用Docker Compose（推荐）
docker-compose up -d

# 或者直接运行
docker run -d -p 5000:5000 --name flash-todo flash-todo
```

### 3. 查看日志
```bash
docker-compose logs -f todo-app
```

## 📊 数据库管理

### 数据库操作
```bash
# 初始化数据库
python migrations.py init

# 执行迁移
python migrations.py migrate

# 备份数据库
python migrations.py backup

# 恢复数据库
python migrations.py restore backups/todo_backup_20231201_120000.db

# 查看数据库信息
python migrations.py info

# 清空数据库
python migrations.py clear

# 创建示例数据
python migrations.py sample
```

## 🔌 API接口

### 任务管理
- `GET /api/todos` - 获取任务列表
- `POST /api/todos` - 创建任务
- `GET /api/todos/<id>` - 获取单个任务
- `PUT /api/todos/<id>` - 更新任务
- `DELETE /api/todos/<id>` - 删除任务

### 统计信息
- `GET /api/stats` - 获取统计信息

### 分类管理
- `GET /api/categories` - 获取分类列表
- `POST /api/categories` - 创建分类

### 标签管理
- `GET /api/tags` - 获取标签列表
- `POST /api/tags` - 创建标签

## 🏗️ 项目结构

```
flash-todo/
├── app.py                 # 原始应用文件
├── app_new.py            # 新架构应用文件
├── config.py             # 配置文件
├── models.py             # 数据模型
├── services.py           # 业务逻辑服务
├── utils.py              # 工具函数
├── migrations.py         # 数据库迁移脚本
├── requirements.txt      # Python依赖
├── Dockerfile            # Docker配置
├── docker-compose.yml    # Docker Compose配置
├── gunicorn.conf.py      # Gunicorn配置
├── env_example.txt       # 环境变量示例
├── README.md             # 项目说明
├── static/               # 静态文件
│   └── style.css
├── templates/            # 模板文件
│   ├── index.html
│   └── edit.html
├── logs/                 # 日志文件
├── uploads/              # 上传文件
├── backups/              # 数据库备份
└── data/                 # 数据文件
```

## 🔧 配置说明

### 环境变量
- `FLASK_APP` - Flask应用文件
- `FLASK_ENV` - 运行环境（development/production）
- `SECRET_KEY` - 应用密钥
- `DATABASE_URL` - 数据库连接URL
- `LOG_LEVEL` - 日志级别

### 数据库配置
- 开发环境：SQLite
- 生产环境：PostgreSQL（推荐）

### 安全配置
- 请求限流
- CSRF保护
- XSS防护
- SQL注入防护

## 🚀 生产环境部署

### 1. 使用Docker Compose（推荐）
```bash
# 设置环境变量
export SECRET_KEY=your-production-secret-key

# 启动服务
docker-compose up -d

# 查看状态
docker-compose ps
```

### 2. 使用Gunicorn
```bash
# 安装依赖
pip install gunicorn

# 启动服务
gunicorn --config gunicorn.conf.py app_new:create_app()
```

### 3. 使用Nginx反向代理
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 🔍 监控和维护

### 日志管理
- 应用日志：`logs/todo_app.log`
- 访问日志：`logs/access.log`
- 错误日志：`logs/error.log`

### 健康检查
```bash
# 检查应用状态
curl http://localhost:5000/api/stats

# 检查数据库连接
python migrations.py info
```

### 备份策略
```bash
# 自动备份（添加到crontab）
0 2 * * * cd /path/to/flash-todo && python migrations.py backup
```

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📝 更新日志

### v2.0.0 (2024-01-01)
- ✨ 全新架构设计
- 🏗️ 模块化代码结构
- 🔒 增强安全机制
- 📊 完善统计功能
- 🐳 Docker支持
- 📱 响应式设计优化

### v1.0.0 (2023-12-01)
- 🎉 初始版本发布
- ✅ 基础任务管理功能
- 🏷️ 优先级和分类支持

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 联系方式

- 项目主页：[GitHub Repository]
- 问题反馈：[Issues]
- 邮箱：your-email@example.com

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者和用户！

---

⭐ 如果这个项目对你有帮助，请给它一个星标！ 

# 📚 数据库相关代码说明

在 `flash-todo` 项目中，数据库相关的代码主要分布在以下几个文件：

1. **app_basic.py**
   - 使用 `sqlite3` 进行数据库操作。
   - 相关函数和代码片段：
     - `get_db()`：创建并返回数据库连接。
     - `init_db()`：初始化数据库表结构。
     - 路由函数（如 `/`, `/add`, `/toggle/<int:todo_id>`, `/delete/<int:todo_id>`, `/edit/<int:todo_id>`）中均有数据库的增删查改操作。

2. **app.py**
   - 也使用 `sqlite3`，有类似的数据库连接和操作逻辑。
   - `get_db_connection()`：获取数据库连接。
   - 在路由处理函数中执行 SQL 查询和数据插入。

3. **app_simple.py**
   - 使用 `Flask-SQLAlchemy` 进行 ORM 操作。
   - `db = SQLAlchemy(app)` 初始化数据库对象。
   - `Todo` 类定义了任务表的结构。
   - 通过 `db.session` 进行数据库的增删查改。

4. **services.py**
   - 通过 `models` 中的 ORM 类（如 `Todo`）进行更复杂的数据库操作和业务逻辑封装。
   - 例如 `TodoService.get_all_todos()` 方法，支持过滤、排序等。

5. **models.py**
   - 这里通常会定义所有 ORM 的数据表结构（如 `Todo`, `Category`, `Tag` 等），具体内容可进一步查看。

这些文件共同实现了数据库的连接、表结构定义、数据的增删查改等功能。你可以根据具体需求，进一步查看某个文件的详细实现。需要详细代码或某一部分的解释可以随时告诉我！ 