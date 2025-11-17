#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库连接配置模块
支持TaurusDB SSL连接
"""

import os
import pymysql
from contextlib import contextmanager
from typing import Dict, Any, Optional, Tuple, List
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseConfig:
    """数据库配置类"""
    
    def __init__(self):
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = int(os.getenv('DB_PORT', 3306))
        self.user = os.getenv('DB_USER', 'root')
        self.password = os.getenv('DB_PASSWORD', '')
        self.database = os.getenv('DB_NAME', 'lab_management_system')
        self.charset = 'utf8mb4'
        
        # SSL配置
        self.ssl_enabled = os.getenv('DB_SSL_ENABLED', 'false').lower() == 'true'
        self.ssl_ca_path = os.getenv('DB_SSL_CA_PATH', './certs/ca-bundle.pem')
        self.ssl_cert_path = os.getenv('DB_SSL_CERT_PATH')
        self.ssl_key_path = os.getenv('DB_SSL_KEY_PATH')
        self.ssl_verify_cert = os.getenv('DB_SSL_REJECT_UNAUTHORIZED', 'true').lower() == 'true'
    
    def get_ssl_config(self) -> Optional[Dict[str, Any]]:
        """获取SSL配置"""
        if not self.ssl_enabled:
            return None
        
        ssl_config = {}
        
        # CA证书配置
        if self.ssl_ca_path and os.path.exists(self.ssl_ca_path):
            ssl_config['ca'] = self.ssl_ca_path
            logger.info(f"SSL CA证书已加载: {self.ssl_ca_path}")
        else:
            logger.warning(f"SSL CA证书文件不存在: {self.ssl_ca_path}")
        
        # 客户端证书配置（可选）
        if self.ssl_cert_path and os.path.exists(self.ssl_cert_path):
            ssl_config['cert'] = self.ssl_cert_path
        
        # 客户端私钥配置（可选）
        if self.ssl_key_path and os.path.exists(self.ssl_key_path):
            ssl_config['key'] = self.ssl_key_path
        
        # 证书验证配置
        ssl_config['check_hostname'] = self.ssl_verify_cert
        ssl_config['verify_mode'] = 2 if self.ssl_verify_cert else 0  # ssl.CERT_REQUIRED : ssl.CERT_NONE
        
        return ssl_config
    
    def get_connection_config(self) -> Dict[str, Any]:
        """获取数据库连接配置"""
        config = {
            'host': self.host,
            'port': self.port,
            'user': self.user,
            'password': self.password,
            'database': self.database,
            'charset': self.charset,
            'autocommit': False,
            'connect_timeout': 60,
            'read_timeout': 60,
            'write_timeout': 60,
        }
        
        # 添加SSL配置
        ssl_config = self.get_ssl_config()
        if ssl_config:
            config['ssl'] = ssl_config
            logger.info("SSL连接已启用")
        
        return config

# 全局数据库配置实例
db_config = DatabaseConfig()

def get_connection():
    """获取数据库连接"""
    try:
        connection = pymysql.connect(**db_config.get_connection_config())
        return connection
    except Exception as e:
        logger.error(f"数据库连接失败: {str(e)}")
        raise

@contextmanager
def get_db_connection():
    """数据库连接上下文管理器"""
    connection = None
    try:
        connection = get_connection()
        yield connection
    except Exception as e:
        if connection:
            connection.rollback()
        logger.error(f"数据库操作失败: {str(e)}")
        raise
    finally:
        if connection:
            connection.close()

def execute_query(sql: str, params: Optional[Tuple] = None) -> Dict[str, Any]:
    """执行查询SQL"""
    try:
        with get_db_connection() as conn:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(sql, params or ())
                result = cursor.fetchall()
                return {
                    'success': True,
                    'data': result,
                    'count': len(result)
                }
    except Exception as e:
        logger.error(f"SQL查询执行失败: {sql}, 参数: {params}, 错误: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'data': []
        }

def execute_update(sql: str, params: Optional[Tuple] = None) -> Dict[str, Any]:
    """执行更新SQL（INSERT, UPDATE, DELETE）"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                affected_rows = cursor.execute(sql, params or ())
                conn.commit()
                return {
                    'success': True,
                    'affected_rows': affected_rows,
                    'last_insert_id': cursor.lastrowid
                }
    except Exception as e:
        logger.error(f"SQL更新执行失败: {sql}, 参数: {params}, 错误: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'affected_rows': 0
        }

def execute_transaction(queries: List[Tuple[str, Optional[Tuple]]]) -> Dict[str, Any]:
    """执行事务"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                results = []
                for sql, params in queries:
                    affected_rows = cursor.execute(sql, params or ())
                    results.append({
                        'sql': sql,
                        'affected_rows': affected_rows,
                        'last_insert_id': cursor.lastrowid
                    })
                conn.commit()
                return {
                    'success': True,
                    'results': results
                }
    except Exception as e:
        logger.error(f"事务执行失败: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'results': []
        }

def execute_paginated_query(sql: str, params: Optional[Tuple] = None, 
                          page: int = 1, page_size: int = 10) -> Dict[str, Any]:
    """执行分页查询"""
    try:
        # 计算偏移量
        offset = (page - 1) * page_size
        
        # 构建分页SQL
        paginated_sql = f"{sql} LIMIT %s OFFSET %s"
        paginated_params = list(params or ()) + [page_size, offset]
        
        # 执行分页查询
        with get_db_connection() as conn:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                # 获取总数
                count_sql = f"SELECT COUNT(*) as total FROM ({sql}) as count_table"
                cursor.execute(count_sql, params or ())
                total = cursor.fetchone()['total']
                
                # 获取分页数据
                cursor.execute(paginated_sql, paginated_params)
                data = cursor.fetchall()
                
                return {
                    'success': True,
                    'data': data,
                    'pagination': {
                        'page': page,
                        'page_size': page_size,
                        'total': total,
                        'total_pages': (total + page_size - 1) // page_size
                    }
                }
    except Exception as e:
        logger.error(f"分页查询执行失败: {sql}, 参数: {params}, 错误: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'data': [],
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total': 0,
                'total_pages': 0
            }
        }

def test_connection() -> bool:
    """测试数据库连接"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                if result:
                    logger.info("数据库连接测试成功")
                    return True
        return False
    except Exception as e:
        logger.error(f"数据库连接测试失败: {str(e)}")
        return False