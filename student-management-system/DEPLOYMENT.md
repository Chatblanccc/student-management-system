# 学生数据管理系统 Docker 部署指南

## 📋 系统要求

### 硬件要求
- CPU: 2核心以上
- 内存: 4GB以上
- 存储: 20GB以上可用空间
- 网络: 稳定的互联网连接

### 软件要求
- Docker Engine 20.10+
- Docker Compose 2.0+
- Git (用于代码管理)

### 支持的操作系统
- Linux (Ubuntu 20.04+, CentOS 7+, Debian 10+)
- Windows 10/11 (with Docker Desktop)
- macOS 10.15+ (with Docker Desktop)

## 🚀 快速部署

### 方法一：一键部署脚本

#### Linux/macOS
```bash
# 赋予脚本执行权限
chmod +x deploy.sh
chmod +x manage-docker.sh

# 运行部署脚本
./deploy.sh
```

#### Windows
```batch
# 直接运行部署脚本
deploy.bat
```

### 方法二：手动部署

1. **克隆项目**
```bash
git clone <your-repository-url>
cd <project-directory>
```

2. **创建环境变量文件**
```bash
cp .env.example .env
# 编辑 .env 文件，修改相关配置
```

3. **创建必要目录**
```bash
mkdir -p backend/logs backend/media backend/staticfiles
```

4. **构建并启动服务**
```bash
docker-compose build
docker-compose up -d
```

5. **运行数据库迁移**
```bash
docker-compose exec backend python manage.py migrate
```

6. **创建超级用户**
```bash
docker-compose exec backend python manage.py createsuperuser
```

## 🛠️ 配置说明

### 环境变量配置

在 `.env` 文件中配置以下参数：

```env
# 数据库配置
DB_PASSWORD=your_secure_password
DB_NAME=DataSystem
DB_USER=root
DB_HOST=db
DB_PORT=3306

# Django配置
SECRET_KEY=your_secret_key_here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

# 安全配置
CORS_ALLOWED_ORIGINS=http://localhost,https://your-domain.com
```

### 生产环境配置

1. **修改数据库密码**
   - 将 `DB_PASSWORD` 修改为强密码
   - 确保密码包含大小写字母、数字和特殊字符

2. **更新Django密钥**
   - 生成新的 `SECRET_KEY`
   - 可以使用在线工具或Django命令生成

3. **配置域名**
   - 将 `ALLOWED_HOSTS` 修改为实际域名
   - 更新 `CORS_ALLOWED_ORIGINS` 为实际前端域名

4. **SSL证书配置**
   - 如需HTTPS，请配置SSL证书
   - 修改nginx配置以支持HTTPS

## 📊 服务管理

### 使用管理脚本

```bash
# 查看所有可用命令
./manage-docker.sh help

# 启动服务
./manage-docker.sh start

# 停止服务
./manage-docker.sh stop

# 查看服务状态
./manage-docker.sh status

# 查看日志
./manage-docker.sh logs

# 进入后端容器
./manage-docker.sh backend

# 数据库备份
./manage-docker.sh backup

# 健康检查
./manage-docker.sh health
```

### 常用Docker Compose命令

```bash
# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f [service_name]

# 重启特定服务
docker-compose restart [service_name]

# 更新服务
docker-compose pull
docker-compose up -d

# 清理资源
docker-compose down --volumes --remove-orphans
```

## 🌐 访问应用

### 默认访问地址
- **前端应用**: http://localhost
- **后端API**: http://localhost/api/
- **管理后台**: http://localhost/api/admin/
- **数据库**: localhost:3306

### 默认登录信息
- 管理员账户需要通过 `createsuperuser` 命令创建
- 数据库root密码在 `.env` 文件中配置

## 🔧 故障排除

### 常见问题

1. **端口冲突**
   - 检查80、8000、3306端口是否被占用
   - 修改 `docker-compose.yml` 中的端口映射

2. **数据库连接失败**
   - 检查数据库容器是否正常启动
   - 验证数据库密码和连接配置

3. **前端无法访问后端API**
   - 检查nginx配置是否正确
   - 验证后端服务是否正常运行

4. **权限问题**
   - 确保目录权限正确
   - 检查Docker容器的用户权限

### 调试命令

```bash
# 查看容器日志
docker-compose logs [service_name]

# 进入容器调试
docker-compose exec [service_name] /bin/bash

# 检查网络连接
docker-compose exec frontend ping backend

# 验证数据库连接
docker-compose exec backend python manage.py dbshell
```

## 📈 性能优化

### 生产环境优化

1. **数据库优化**
   - 配置MySQL缓存
   - 添加数据库索引
   - 定期清理日志

2. **静态文件优化**
   - 启用Gzip压缩
   - 配置CDN加速
   - 设置缓存策略

3. **容器资源限制**
   ```yaml
   services:
     backend:
       deploy:
         resources:
           limits:
             memory: 512M
             cpus: '0.5'
   ```

## 🔒 安全配置

### 基本安全措施

1. **更改默认密码**
   - 数据库root密码
   - Django超级用户密码

2. **网络安全**
   - 配置防火墙规则
   - 仅开放必要端口
   - 使用HTTPS

3. **容器安全**
   - 定期更新镜像
   - 扫描安全漏洞
   - 限制容器权限

## 📦 备份与恢复

### 数据备份

```bash
# 自动备份
./manage-docker.sh backup

# 手动备份
docker-compose exec db mysqldump -u root -p DataSystem > backup.sql
```

### 数据恢复

```bash
# 恢复数据库
./manage-docker.sh restore backup.sql

# 手动恢复
docker-compose exec -T db mysql -u root -p DataSystem < backup.sql
```

## 📞 技术支持

如果在部署过程中遇到问题，请：

1. 查看日志文件确定错误原因
2. 检查系统资源是否充足
3. 验证网络连接是否正常
4. 参考官方文档进行配置

---

## 🎉 部署完成

部署成功后，您的学生数据管理系统将在以下地址可访问：
- 主应用: http://localhost
- API文档: http://localhost/api/
- 管理后台: http://localhost/api/admin/

祝您使用愉快！ 🚀 