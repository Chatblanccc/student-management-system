#!/bin/bash

# 学生数据管理系统 Docker 部署脚本
set -e

echo "🚀 开始部署学生数据管理系统..."

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

# 创建必要的目录
echo "📁 创建必要的目录..."
mkdir -p backend/logs
mkdir -p backend/media
mkdir -p backend/staticfiles

# 复制环境变量文件（如果不存在）
if [ ! -f .env ]; then
    echo "📝 创建环境变量文件..."
    cat > .env << EOF
# 数据库配置
DB_PASSWORD=1997yx0912
DB_NAME=DataSystem
DB_USER=root
DB_HOST=db
DB_PORT=3306

# Django配置
SECRET_KEY=django-insecure-yy)&3!0l7+6^!-sf9n_0=ee0g--^&l4+sy*5ruf*lfrz^02h^v
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,backend,frontend

# 安全配置（生产环境请修改）
CORS_ALLOWED_ORIGINS=http://localhost,http://127.0.0.1
EOF
    echo "✅ 环境变量文件已创建，请根据需要修改 .env 文件"
fi

# 停止现有容器
echo "🛑 停止现有容器..."
docker-compose down

# 构建并启动服务
echo "🔨 构建Docker镜像..."
docker-compose build --no-cache

echo "🗄️ 启动数据库服务..."
docker-compose up -d db redis

# 等待数据库启动
echo "⏳ 等待数据库启动..."
sleep 30

# 运行数据库迁移
echo "🗄️ 运行数据库迁移..."
docker-compose run --rm backend python manage.py makemigrations
docker-compose run --rm backend python manage.py migrate

# 创建超级用户（可选）
echo "👤 是否创建Django超级用户？(y/n)"
read -r create_superuser
if [ "$create_superuser" = "y" ] || [ "$create_superuser" = "Y" ]; then
    docker-compose run --rm backend python manage.py createsuperuser
fi

# 启动所有服务
echo "🚀 启动所有服务..."
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 15

# 检查服务状态
echo "🔍 检查服务状态..."
docker-compose ps

# 健康检查
echo "🏥 进行健康检查..."
if curl -f http://localhost/api/health/ > /dev/null 2>&1; then
    echo "✅ 后端服务健康检查通过"
else
    echo "⚠️ 后端服务健康检查失败，请检查日志"
fi

if curl -f http://localhost/ > /dev/null 2>&1; then
    echo "✅ 前端服务健康检查通过"
else
    echo "⚠️ 前端服务健康检查失败，请检查日志"
fi

echo ""
echo "🎉 部署完成！"
echo "📍 访问地址: http://localhost"
echo "🔧 管理后台: http://localhost/api/admin/"
echo "📊 查看日志: docker-compose logs -f"
echo "🛑 停止服务: docker-compose down"
echo "" 