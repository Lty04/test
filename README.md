# 大学外卖系统

## 项目简介
这是一个基于 Python Flask 的大学校园外卖系统，支持学生订餐、商家管理、订单配送等功能。

## 功能特性
- 用户注册与登录（学生、商家、配送员）
- 餐厅和菜品管理
- 购物车和订单管理
- 订单状态跟踪
- 配送管理
- 评价系统

## 技术栈
- 后端：Flask + SQLAlchemy
- 数据库：SQLite（可切换到 MySQL/PostgreSQL）
- 前端：HTML + CSS + JavaScript（Bootstrap）
- 认证：Flask-Login

## 目录结构
```
university_food_delivery/
├── app.py                 # 主应用入口
├── config.py              # 配置文件
├── models.py              # 数据模型
├── routes/                # 路由模块
│   ├── __init__.py
│   ├── auth.py           # 认证路由
│   ├── restaurant.py     # 餐厅路由
│   ├── order.py          # 订单路由
│   └── user.py           # 用户路由
├── templates/             # HTML 模板
├── static/               # 静态文件
│   ├── css/
│   ├── js/
│   └── images/
└── requirements.txt      # 依赖包
```

## 快速开始

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 初始化数据库：
```bash
python app.py
```

3. 访问系统：
```
http://localhost:5000
```

## 默认账号
- 学生账号：student / student123
- 商家账号：restaurant / restaurant123
- 配送员账号：delivery / delivery123
- 管理员账号：admin / admin123
