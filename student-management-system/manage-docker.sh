#!/bin/bash

# 学生数据管理系统 Docker 管理脚本

show_help() {
    echo "学生数据管理系统 Docker 管理脚本"
    echo ""
    echo "用法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  start       启动所有服务"
    echo "  stop        停止所有服务"
    echo "  restart     重启所有服务"
    echo "  status      查看服务状态"
    echo "  logs        查看所有服务日志"
    echo "  logs-f      实时查看日志"
    echo "  backend     进入后端容器"
    echo "  frontend    进入前端容器"
    echo "  db          进入数据库容器"
    echo "  migrate     运行数据库迁移"
    echo "  backup      备份数据库"
    echo "  restore     恢复数据库"
    echo "  clean       清理未使用的镜像和容器"
    echo "  rebuild     重新构建并启动"
    echo "  health      健康检查"
    echo "  update      更新服务"
    echo "  help        显示此帮助信息"
    echo ""
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker未安装"
        exit 1
    fi
    if ! command -v docker-compose &> /dev/null; then
        echo "❌ Docker Compose未安装"
        exit 1
    fi
}

case "$1" in
    "start")
        echo "🚀 启动所有服务..."
        docker-compose up -d
        echo "✅ 服务已启动"
        ;;
    "stop")
        echo "🛑 停止所有服务..."
        docker-compose down
        echo "✅ 服务已停止"
        ;;
    "restart")
        echo "🔄 重启所有服务..."
        docker-compose restart
        echo "✅ 服务已重启"
        ;;
    "status")
        echo "📊 服务状态:"
        docker-compose ps
        ;;
    "logs")
        echo "📋 查看服务日志:"
        docker-compose logs --tail=100
        ;;
    "logs-f")
        echo "📋 实时查看服务日志 (Ctrl+C 退出):"
        docker-compose logs -f
        ;;
    "backend")
        echo "🐍 进入后端容器..."
        docker-compose exec backend bash
        ;;
    "frontend")
        echo "🌐 进入前端容器..."
        docker-compose exec frontend sh
        ;;
    "db")
        echo "🗄️ 进入数据库容器..."
        docker-compose exec db mysql -u root -p DataSystem
        ;;
    "migrate")
        echo "🗄️ 运行数据库迁移..."
        docker-compose exec backend python manage.py makemigrations
        docker-compose exec backend python manage.py migrate
        echo "✅ 迁移完成"
        ;;
    "backup")
        echo "💾 备份数据库..."
        timestamp=$(date +"%Y%m%d_%H%M%S")
        docker-compose exec db mysqldump -u root -p1997yx0912 DataSystem > "backup_${timestamp}.sql"
        echo "✅ 数据库已备份到 backup_${timestamp}.sql"
        ;;
    "restore")
        if [ -z "$2" ]; then
            echo "❌ 请指定备份文件: $0 restore backup_file.sql"
            exit 1
        fi
        echo "🔄 恢复数据库..."
        docker-compose exec -T db mysql -u root -p1997yx0912 DataSystem < "$2"
        echo "✅ 数据库恢复完成"
        ;;
    "clean")
        echo "🧹 清理未使用的镜像和容器..."
        docker system prune -f
        docker volume prune -f
        echo "✅ 清理完成"
        ;;
    "rebuild")
        echo "🔨 重新构建并启动..."
        docker-compose down
        docker-compose build --no-cache
        docker-compose up -d
        echo "✅ 重新构建完成"
        ;;
    "health")
        echo "🏥 进行健康检查..."
        echo "检查后端服务..."
        if curl -f http://localhost/api/health/ > /dev/null 2>&1; then
            echo "✅ 后端服务正常"
        else
            echo "❌ 后端服务异常"
        fi
        
        echo "检查前端服务..."
        if curl -f http://localhost/ > /dev/null 2>&1; then
            echo "✅ 前端服务正常"
        else
            echo "❌ 前端服务异常"
        fi
        
        echo "检查数据库服务..."
        if docker-compose exec db mysqladmin ping -h localhost -u root -p1997yx0912 > /dev/null 2>&1; then
            echo "✅ 数据库服务正常"
        else
            echo "❌ 数据库服务异常"
        fi
        ;;
    "update")
        echo "🔄 更新服务..."
        git pull
        docker-compose down
        docker-compose build --no-cache
        docker-compose up -d
        echo "✅ 更新完成"
        ;;
    "help"|""|*)
        show_help
        ;;
esac 