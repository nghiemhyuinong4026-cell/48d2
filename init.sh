#!/bin/bash

echo "========================================"
echo "CAPA 系统初始化脚本"
echo "========================================"

set -e

echo ""
echo "[1/4] 启动 Docker 服务..."
docker-compose up -d --build

echo ""
echo "[2/4] 等待 PostgreSQL 就绪..."
sleep 10

echo ""
echo "[3/4] 运行数据库迁移..."
docker-compose exec -T web python manage.py migrate

echo ""
echo "[4/4] 种子测试账号..."
docker-compose exec -T web python manage.py seed_users

echo ""
echo "========================================"
echo "初始化完成！"
echo "========================================"
echo ""
echo "服务地址："
echo "  - API: http://localhost:8000/"
echo "  - Admin: http://localhost:8000/admin/"
echo ""
echo "测试账号："
echo "  - 质量工程师: quality.engineer@example.com / Test@1234"
echo "  - 责任人: responsible.person@example.com / Test@1234"
echo "  - QA: qa@example.com / Test@1234"
echo "  - 审计员: auditor@example.com / Test@1234"
echo "  - 管理员: admin@example.com / Admin@1234"
echo ""
echo "常用命令："
echo "  - 查看日志: docker-compose logs -f web"
echo "  - 停止服务: docker-compose down"
echo "  - 运行逾期扫描: docker-compose exec web python manage.py scan_overdue"
echo ""
