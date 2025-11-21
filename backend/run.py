#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实验室管理系统后端启动脚本
"""

import os
import sys
import logging
from dotenv import load_dotenv

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')))

# 加载环境变量
load_dotenv()

# 预先创建日志目录，避免 FileHandler 初始化时报错
LOG_FILE = os.getenv('LOG_FILE', 'logs/app.log')
LOG_DIR = os.path.dirname(LOG_FILE)
if LOG_DIR and not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR, exist_ok=True)

# 配置日志
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_FILE, encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

def create_app():
    """创建Flask应用"""
    try:
        # 由于同时存在包目录 `app/` 与同名模块 `app.py`，直接 `import app`
        # 会导入包而非模块。这里通过路径显式加载 `app.py` 并调用其中的 `create_app`。
        import importlib.util
        module_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.py')
        spec = importlib.util.spec_from_file_location('backend_app', module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.create_app()
    except Exception as e:
        logger.error(f"导入应用失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    # 创建应用
    app = create_app()
    
    # 获取配置
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = True
    
    logger.info(f"启动实验室管理系统后端服务...")
    logger.info(f"服务地址: http://{host}:{port}")
    logger.info(f"调试模式: {debug}")
    
    try:
        app.run(host=host, port=port, debug=debug)
    except Exception as e:
        logger.error(f"启动服务失败: {e}")
        sys.exit(1)