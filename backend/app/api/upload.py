import os
import uuid
from flask import Blueprint, request, current_app
from werkzeug.utils import secure_filename
from app.utils.auth import require_auth
from app.utils.response import success_response, error_response
from backend.database import execute_update

upload_bp = Blueprint('upload', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

import shutil

@upload_bp.route('/avatar', methods=['POST'])
@require_auth
def upload_avatar():
    """上传用户头像"""
    try:
        if 'file' not in request.files:
            return error_response("没有文件部分")
        
        file = request.files['file']
        
        if file.filename == '':
            return error_response("未选择文件")
        
        if file and allowed_file(file.filename):
            # 计算路径
            # current_dir = .../backend/app/api
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # backend_dir = .../backend
            backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
            # project_root = .../lab-management-system
            project_root = os.path.dirname(backend_dir)
            
            # 前端目录路径
            frontend_public_avatars = os.path.join(project_root, 'frontend', 'public', 'avatars')
            frontend_dist_avatars = os.path.join(project_root, 'frontend', 'dist', 'avatars')
            
            # 确保 public/avatars 存在
            if not os.path.exists(frontend_public_avatars):
                os.makedirs(frontend_public_avatars)
                
            # 生成文件名
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            
            # 保存到 frontend/public/avatars
            public_file_path = os.path.join(frontend_public_avatars, unique_filename)
            file.save(public_file_path)
            
            # 如果 frontend/dist 存在，也保存一份到 frontend/dist/avatars
            # 这样可以在生产环境构建后立即生效，无需重新构建
            if os.path.exists(os.path.dirname(frontend_dist_avatars)):
                if not os.path.exists(frontend_dist_avatars):
                    os.makedirs(frontend_dist_avatars)
                dist_file_path = os.path.join(frontend_dist_avatars, unique_filename)
                shutil.copy2(public_file_path, dist_file_path)
            
            # 生成访问URL
            # 前端 public 目录下的文件可以直接通过 /avatars/... 访问
            avatar_url = f"/avatars/{unique_filename}"
            
            # 更新用户信息
            current_user = request.current_user
            user_id = current_user.get('id') or current_user.get('user_id')
            
            update_sql = "UPDATE users SET avatar = %s WHERE id = %s"
            result = execute_update(update_sql, (avatar_url, user_id))
            
            if result['success']:
                return success_response({'url': avatar_url}, "头像上传成功")
            else:
                return error_response("头像更新失败")
                
        return error_response("不支持的文件类型，请上传图片")
        
    except Exception as e:
        return error_response(f"上传系统错误: {str(e)}")
