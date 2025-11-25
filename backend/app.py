#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高校实验室预约与设备管理系统 - Python后端
主应用入口文件
"""

import os
import sys
from flask import Flask, jsonify, redirect
from flask_cors import CORS
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def create_app():
    """创建Flask应用实例"""
    # 确保项目根目录在模块搜索路径中，保证包导入稳定
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if PROJECT_ROOT not in sys.path:
        sys.path.insert(0, PROJECT_ROOT)
    app = Flask(__name__)
    
    # 配置
    app.config['SECRET_KEY'] = os.getenv('JWT_SECRET', 'lab_management_jwt_secret_2024_secure_key')
    app.config['JSON_AS_ASCII'] = False  # 支持中文JSON响应
    
    # 启用CORS
    CORS(app, 
         origins=["http://localhost:5173", "http://localhost:8080"] if os.getenv('NODE_ENV') == 'production' 
         else "*",
         supports_credentials=True)
    
    # 启动时执行轻量数据库迁移，确保关键列存在
    try:
        from app.db_migration import run as run_db_migration, _ensure_reservations_columns
        run_db_migration()
        try:
            _ensure_reservations_columns()
        except Exception:
            pass
    except Exception:
        # 迁移失败不阻止应用启动，详见日志
        pass

    # 注册蓝图
    from app.api.auth import auth_bp
    from app.api.users import users_bp
    from app.api.laboratories import laboratories_bp
    from app.api.equipment import equipment_bp
    from app.api.reservations import reservations_bp
    from app.api.courses import courses_bp
    from app.api.maintenance import maintenance_bp
    from app.api.consumables import consumables_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(laboratories_bp, url_prefix='/api/laboratories')
    # 为历史前端路径提供别名：/api/labs -> /api/laboratories（使用 307 保留方法转发）
    @app.route('/api/labs', defaults={'subpath': ''}, methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
    @app.route('/api/labs/<path:subpath>', methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
    def labs_alias(subpath):
        # 避免空子路径导致尾部斜杠，造成 404
        target = '/api/laboratories' + (f'/{subpath}' if subpath else '')
        return redirect(target, code=307)
    app.register_blueprint(equipment_bp, url_prefix='/api/equipment')
    # 维修记录相关接口
    app.register_blueprint(maintenance_bp, url_prefix='/api/equipment/maintenance')
    # 耗材相关接口
    app.register_blueprint(consumables_bp, url_prefix='/api/consumables')
    app.register_blueprint(reservations_bp, url_prefix='/api/reservations')
    app.register_blueprint(courses_bp, url_prefix='/api/courses')
    
    # 健康检查端点
    @app.route('/health', methods=['GET'])
    def health_check():
        """健康检查接口"""
        return jsonify({
            'status': 'OK',
            'message': '实验室管理系统运行正常',
            'version': '2.0.0-python'
        })
    
    # 全局错误处理
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': '接口不存在', 'code': 404}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': '服务器内部错误', 'code': 500}), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    
    # 测试数据库连接
    from backend.database import test_connection
    if test_connection():
        print("✅ 数据库连接成功")
    else:
        print("❌ 数据库连接失败")
    
    # 启动应用
    port = int(os.getenv('PORT', 3000))
    debug = os.getenv('NODE_ENV', 'development') == 'development'
    
    print(f"🚀 服务器启动在端口 {port}")
    print(f"🌐 健康检查: http://localhost:{port}/health")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
