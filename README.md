# CAPA 生产质量异常整改系统

基于 Django 5 + DRF 的 CAPA (Corrective and Preventive Action) 生产质量异常整改系统 MVP。

## 技术栈

- **Python**: 3.12
- **Django**: 5.x
- **Django REST Framework**: 3.15+
- **SimpleJWT**: 认证
- **PostgreSQL**: 15

## 快速启动

### 构建镜像

```bash
docker build -t capa-quality-system .
```

### 启动容器

```bash
docker run -d -p 18119:8000 --name docker-question-119 capa-quality-system
```

### 访问服务

- API 服务: http://127.0.0.1:18119/
- Admin 后台: http://127.0.0.1:18119/admin/

## 测试账号

| 角色 | 邮箱 | 密码 |
|------|------|------|
| 质量工程师 | quality.engineer@example.com | Test@1234 |
| 责任人 | responsible.person@example.com | Test@1234 |
| QA | qa@example.com | Test@1234 |
| 审计员 | auditor@example.com | Test@1234 |
| 管理员 | admin@example.com | Admin@1234 |

## API 接口

### 1. 登录
```bash
curl -X POST http://127.0.0.1:18119/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"email": "quality.engineer@example.com", "password": "Test@1234"}'
```

### 2. 质量异常列表
```bash
curl http://127.0.0.1:18119/api/quality-issues/ \
  -H "Authorization: Bearer $TOKEN"
```

### 3. 创建质量异常
```bash
curl -X POST http://127.0.0.1:18119/api/quality-issues/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "title": "生产线产品外观缺陷",
    "description": "A1生产线生产的产品发现多处外观刮伤缺陷",
    "severity": "major"
  }'
```

## 常用管理命令

```bash
# 查看日志
docker logs -f docker-question-119

# 停止容器
docker stop docker-question-119

# 删除容器
docker rm docker-question-119

# 进入容器
docker exec -it docker-question-119 bash
```