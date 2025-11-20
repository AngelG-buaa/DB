<template>
  <div class="profile-container">
    <el-card class="profile-card">
      <template #header>
        <div class="card-header">
          <span>个人资料</span>
        </div>
      </template>
      
      <div class="profile-content">
        <!-- 头像区域 -->
        <div class="avatar-section">
          <el-avatar
            :size="120"
            :src="userInfo.avatar"
            class="user-avatar"
          >
            <el-icon><User /></el-icon>
          </el-avatar>
          
          <el-upload
            class="avatar-uploader"
            action="/api/upload/avatar"
            :headers="uploadHeaders"
            :show-file-list="false"
            :on-success="handleAvatarSuccess"
            :before-upload="beforeAvatarUpload"
          >
            <el-button size="small" type="primary">更换头像</el-button>
          </el-upload>
        </div>
        
        <!-- 基本信息 -->
        <div class="info-section">
          <el-form
            ref="profileFormRef"
            :model="profileForm"
            :rules="profileRules"
            label-width="100px"
            class="profile-form"
          >
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="用户名">
                  <el-input v-model="profileForm.username" disabled />
                </el-form-item>
              </el-col>
              
              <el-col :span="12">
                <el-form-item label="用户类型">
                  <el-tag :type="userTypeTagType">{{ userTypeText }}</el-tag>
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="真实姓名" prop="realName">
                  <el-input
                    v-model="profileForm.realName"
                    :disabled="!editMode"
                    clearable
                  />
                </el-form-item>
              </el-col>
              
              <el-col :span="12">
                <el-form-item label="邮箱" prop="email">
                  <el-input
                    v-model="profileForm.email"
                    :disabled="!editMode"
                    clearable
                  />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="手机号" prop="phone">
                  <el-input
                    v-model="profileForm.phone"
                    :disabled="!editMode"
                    clearable
                  />
                </el-form-item>
              </el-col>
              
              <el-col :span="12">
                <el-form-item label="学院" prop="department">
                  <el-select
                    v-model="profileForm.department"
                    :disabled="!editMode"
                    placeholder="请选择学院"
                    style="width: 100%"
                  >
                    <el-option label="计算机科学与技术学院" value="计算机科学与技术学院" />
                    <el-option label="电子工程学院" value="电子工程学院" />
                    <el-option label="物理学院" value="物理学院" />
                    <el-option label="化学学院" value="化学学院" />
                    <el-option label="生物学院" value="生物学院" />
                    <el-option label="数学学院" value="数学学院" />
                    <el-option label="材料科学与工程学院" value="材料科学与工程学院" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
            
            <!-- 学生特有信息 -->
            <template v-if="userInfo.user_type === 'student'">
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="学号">
                    <el-input v-model="profileForm.studentId" disabled />
                  </el-form-item>
                </el-col>
                
                <el-col :span="12">
                  <el-form-item label="专业" prop="major">
                    <el-input
                      v-model="profileForm.major"
                      :disabled="!editMode"
                      clearable
                    />
                  </el-form-item>
                </el-col>
              </el-row>
              
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="年级" prop="grade">
                    <el-select
                      v-model="profileForm.grade"
                      :disabled="!editMode"
                      placeholder="请选择年级"
                      style="width: 100%"
                    >
                      <el-option
                        v-for="year in gradeOptions"
                        :key="year"
                        :label="`${year}级`"
                        :value="year"
                      />
                    </el-select>
                  </el-form-item>
                </el-col>
              </el-row>
            </template>
            
            <!-- 教师特有信息 -->
            <template v-if="userInfo.user_type === 'teacher'">
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="工号">
                    <el-input v-model="profileForm.employeeId" disabled />
                  </el-form-item>
                </el-col>
              </el-row>
            </template>
            
            <el-form-item>
              <el-button
                v-if="!editMode"
                type="primary"
                @click="enableEdit"
              >
                编辑资料
              </el-button>
              
              <template v-else>
                <el-button
                  type="primary"
                  :loading="saveLoading"
                  @click="saveProfile"
                >
                  保存
                </el-button>
                <el-button @click="cancelEdit">取消</el-button>
              </template>
            </el-form-item>
          </el-form>
        </div>
      </div>
    </el-card>
    
    <!-- 修改密码 -->
    <el-card class="password-card">
      <template #header>
        <div class="card-header">
          <span>修改密码</span>
        </div>
      </template>
      
      <el-form
        ref="passwordFormRef"
        :model="passwordForm"
        :rules="passwordRules"
        label-width="100px"
        class="password-form"
      >
        <el-form-item label="当前密码" prop="currentPassword">
          <el-input
            v-model="passwordForm.currentPassword"
            type="password"
            placeholder="请输入当前密码"
            show-password
            clearable
          />
        </el-form-item>
        
        <el-form-item label="新密码" prop="newPassword">
          <el-input
            v-model="passwordForm.newPassword"
            type="password"
            placeholder="请输入新密码"
            show-password
            clearable
          />
        </el-form-item>
        
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="passwordForm.confirmPassword"
            type="password"
            placeholder="请再次输入新密码"
            show-password
            clearable
          />
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            :loading="passwordLoading"
            @click="changePassword"
          >
            修改密码
          </el-button>
          <el-button @click="resetPasswordForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 账户统计 -->
    <el-card class="stats-card">
      <template #header>
        <div class="card-header">
          <span>账户统计</span>
        </div>
      </template>
      
      <el-row :gutter="20" class="stats-row">
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-value">{{ userStats.totalReservations }}</div>
            <div class="stat-label">总预约次数</div>
          </div>
        </el-col>
        
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-value">{{ userStats.activeReservations }}</div>
            <div class="stat-label">进行中预约</div>
          </div>
        </el-col>
        
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-value">{{ userStats.completedReservations }}</div>
            <div class="stat-label">已完成预约</div>
          </div>
        </el-col>
        
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-value">{{ userStats.cancelledReservations }}</div>
            <div class="stat-label">已取消预约</div>
          </div>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { User } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { updateUserInfoApi, changePasswordApi } from '@/api/auth'
import { getMyReservationsApi } from '@/api/reservation'

const userStore = useUserStore()

// 响应式数据
const profileFormRef = ref()
const passwordFormRef = ref()
const editMode = ref(false)
const saveLoading = ref(false)
const passwordLoading = ref(false)

const profileForm = reactive({
  username: '',
  realName: '',
  email: '',
  phone: '',
  department: '',
  studentId: '',
  major: '',
  grade: null,
  employeeId: ''
})

const passwordForm = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const userStats = reactive({
  totalReservations: 0,
  activeReservations: 0,
  completedReservations: 0,
  cancelledReservations: 0
})

// 计算属性
const userInfo = computed(() => userStore.userInfo)

const userTypeText = computed(() => {
  const typeMap = {
    admin: '管理员',
    teacher: '教师',
    student: '学生'
  }
  return typeMap[userInfo.value?.role] || '未知'
})

const userTypeTagType = computed(() => {
  const typeMap = {
    admin: 'danger',
    teacher: 'warning',
    student: 'success'
  }
  return typeMap[userInfo.value?.role] || 'info'
})

const gradeOptions = computed(() => {
  const currentYear = new Date().getFullYear()
  return Array.from({ length: 6 }, (_, i) => currentYear - i)
})

const uploadHeaders = computed(() => ({
  Authorization: `Bearer ${userStore.token}`
}))

// 表单验证规则
const profileRules = {
  realName: [
    { required: true, message: '请输入真实姓名', trigger: 'blur' },
    { min: 2, max: 10, message: '姓名长度在 2 到 10 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ],
  department: [
    { required: true, message: '请选择学院', trigger: 'change' }
  ]
}

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== passwordForm.newPassword) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const passwordRules = {
  currentPassword: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度在 6 到 20 个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

// 方法
const initProfileForm = () => {
  const info = userInfo.value
  profileForm.username = info.username || ''
  profileForm.realName = info.real_name || ''
  profileForm.email = info.email || ''
  profileForm.phone = info.phone || ''
  profileForm.department = info.department || ''
  profileForm.studentId = info.student_id || ''
  profileForm.major = info.major || ''
  profileForm.grade = info.grade || null
  profileForm.employeeId = info.employee_id || ''
}

const enableEdit = () => {
  editMode.value = true
}

const cancelEdit = () => {
  editMode.value = false
  initProfileForm()
}

const saveProfile = async () => {
  if (!profileFormRef.value) return
  
  try {
    await profileFormRef.value.validate()
    saveLoading.value = true
    
    const updateData = {
      real_name: profileForm.realName,
      email: profileForm.email,
      phone: profileForm.phone,
      department: profileForm.department
    }
    
    if (userInfo.value.user_type === 'student') {
      updateData.major = profileForm.major
      updateData.grade = profileForm.grade
    }
    
    const response = await updateUserInfoApi(updateData)
    
    if (response.code === 200) {
      await userStore.getUserInfo()
      editMode.value = false
      ElMessage.success('个人资料更新成功')
    }
  } catch (error) {
    console.error('更新个人资料失败:', error)
  } finally {
    saveLoading.value = false
  }
}

const changePassword = async () => {
  if (!passwordFormRef.value) return
  
  try {
    await passwordFormRef.value.validate()
    passwordLoading.value = true
    
    const response = await changePasswordApi({
      current_password: passwordForm.currentPassword,
      new_password: passwordForm.newPassword
    })
    
    if (response.code === 200) {
      resetPasswordForm()
      ElMessage.success('密码修改成功')
    }
  } catch (error) {
    console.error('修改密码失败:', error)
  } finally {
    passwordLoading.value = false
  }
}

const resetPasswordForm = () => {
  passwordForm.currentPassword = ''
  passwordForm.newPassword = ''
  passwordForm.confirmPassword = ''
  if (passwordFormRef.value) {
    passwordFormRef.value.clearValidate()
  }
}

const handleAvatarSuccess = (response) => {
  if (response.code === 200) {
    userStore.updateUserInfo({ avatar: response.data.url })
    ElMessage.success('头像更新成功')
  }
}

const beforeAvatarUpload = (file) => {
  const isJPG = file.type === 'image/jpeg' || file.type === 'image/png'
  const isLt2M = file.size / 1024 / 1024 < 2
  
  if (!isJPG) {
    ElMessage.error('头像图片只能是 JPG/PNG 格式!')
    return false
  }
  if (!isLt2M) {
    ElMessage.error('头像图片大小不能超过 2MB!')
    return false
  }
  return true
}

const loadUserStats = async () => {
  try {
    const res = await getMyReservationsApi({ page: 1, page_size: 100 })
    if (res.code === 200) {
      const list = res.data.list || []
      userStats.totalReservations = list.length
      userStats.activeReservations = list.filter(i => i.status === 'confirmed' || i.status === 'approved').length
      userStats.completedReservations = list.filter(i => i.status === 'completed').length
      userStats.cancelledReservations = list.filter(i => i.status === 'cancelled').length
    }
  } catch (error) {
    
  }
}

// 生命周期
onMounted(() => {
  initProfileForm()
  loadUserStats()
})
</script>

<style lang="scss" scoped>
.profile-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.profile-card,
.password-card,
.stats-card {
  margin-bottom: 20px;
  
  .card-header {
    font-size: 16px;
    font-weight: 600;
    color: #303133;
  }
}

.profile-content {
  display: flex;
  gap: 40px;
  
  .avatar-section {
    flex-shrink: 0;
    text-align: center;
    
    .user-avatar {
      margin-bottom: 16px;
      border: 3px solid #f0f0f0;
    }
    
    .avatar-uploader {
      display: block;
    }
  }
  
  .info-section {
    flex: 1;
    
    .profile-form {
      .el-form-item {
        margin-bottom: 18px;
      }
    }
  }
}

.password-form {
  max-width: 500px;
  
  .el-form-item {
    margin-bottom: 18px;
  }
}

.stats-row {
  .stat-item {
    text-align: center;
    padding: 20px;
    background: #f8f9fa;
    border-radius: 8px;
    
    .stat-value {
      font-size: 28px;
      font-weight: 600;
      color: #409eff;
      margin-bottom: 8px;
    }
    
    .stat-label {
      font-size: 14px;
      color: #909399;
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .profile-content {
    flex-direction: column;
    gap: 20px;
    
    .avatar-section {
      align-self: center;
    }
  }
  
  .stats-row {
    .el-col {
      margin-bottom: 10px;
    }
  }
}
</style>