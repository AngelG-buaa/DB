<template>
  <div class="settings-index">
    <el-row :gutter="20">
      <!-- 左侧菜单 -->
      <el-col :span="6">
        <el-card class="settings-menu">
          <el-menu
            :default-active="activeMenu"
            @select="handleMenuSelect"
            class="settings-menu-list"
          >
            <el-menu-item index="basic">
              <el-icon><Setting /></el-icon>
              <span>基本设置</span>
            </el-menu-item>
            <el-menu-item index="notification">
              <el-icon><Bell /></el-icon>
              <span>通知设置</span>
            </el-menu-item>
            <el-menu-item index="security">
              <el-icon><Lock /></el-icon>
              <span>安全设置</span>
            </el-menu-item>
            <el-menu-item index="backup">
              <el-icon><Download /></el-icon>
              <span>备份设置</span>
            </el-menu-item>
            <el-menu-item index="system">
              <el-icon><Monitor /></el-icon>
              <span>系统信息</span>
            </el-menu-item>
          </el-menu>
        </el-card>
      </el-col>
      
      <!-- 右侧内容 -->
      <el-col :span="18">
        <!-- 基本设置 -->
        <el-card v-show="activeMenu === 'basic'" class="settings-content">
          <template #header>
            <span>基本设置</span>
          </template>
          
          <el-form
            ref="basicFormRef"
            :model="basicSettings"
            :rules="basicRules"
            label-width="150px"
          >
            <el-form-item label="系统名称" prop="system_name">
              <el-input
                v-model="basicSettings.system_name"
                placeholder="请输入系统名称"
                maxlength="100"
              />
            </el-form-item>
            
            <el-form-item label="系统描述" prop="system_description">
              <el-input
                v-model="basicSettings.system_description"
                type="textarea"
                :rows="3"
                placeholder="请输入系统描述"
                maxlength="500"
              />
            </el-form-item>
            
            <el-form-item label="默认预约时长" prop="default_reservation_duration">
              <el-input-number
                v-model="basicSettings.default_reservation_duration"
                :min="1"
                :max="24"
                style="width: 200px"
              />
              <span style="margin-left: 10px">小时</span>
            </el-form-item>
            
            <el-form-item label="预约提前时间" prop="advance_booking_hours">
              <el-input-number
                v-model="basicSettings.advance_booking_hours"
                :min="1"
                :max="168"
                style="width: 200px"
              />
              <span style="margin-left: 10px">小时</span>
            </el-form-item>
            
            <el-form-item label="自动审批" prop="auto_approval">
              <el-switch
                v-model="basicSettings.auto_approval"
                active-text="开启"
                inactive-text="关闭"
              />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="saveBasicSettings" :loading="saving">
                保存设置
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
        
        <!-- 通知设置 -->
        <el-card v-show="activeMenu === 'notification'" class="settings-content">
          <template #header>
            <span>通知设置</span>
          </template>
          
          <el-form :model="notificationSettings" label-width="150px">
            <el-form-item label="邮件通知">
              <el-switch
                v-model="notificationSettings.email_enabled"
                active-text="开启"
                inactive-text="关闭"
              />
            </el-form-item>
            
            <el-form-item v-if="notificationSettings.email_enabled" label="SMTP服务器">
              <el-input
                v-model="notificationSettings.smtp_server"
                placeholder="请输入SMTP服务器地址"
              />
            </el-form-item>
            
            <el-form-item v-if="notificationSettings.email_enabled" label="SMTP端口">
              <el-input-number
                v-model="notificationSettings.smtp_port"
                :min="1"
                :max="65535"
                style="width: 200px"
              />
            </el-form-item>
            
            <el-form-item label="预约提醒">
              <el-switch
                v-model="notificationSettings.reservation_reminder"
                active-text="开启"
                inactive-text="关闭"
              />
            </el-form-item>
            
            <el-form-item label="设备维护提醒">
              <el-switch
                v-model="notificationSettings.maintenance_reminder"
                active-text="开启"
                inactive-text="关闭"
              />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="saveNotificationSettings" :loading="saving">
                保存设置
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
        
        <!-- 安全设置 -->
        <el-card v-show="activeMenu === 'security'" class="settings-content">
          <template #header>
            <span>安全设置</span>
          </template>
          
          <el-form :model="securitySettings" label-width="150px">
            <el-form-item label="密码最小长度">
              <el-input-number
                v-model="securitySettings.min_password_length"
                :min="6"
                :max="20"
                style="width: 200px"
              />
            </el-form-item>
            
            <el-form-item label="密码复杂度">
              <el-checkbox-group v-model="securitySettings.password_requirements">
                <el-checkbox label="uppercase">包含大写字母</el-checkbox>
                <el-checkbox label="lowercase">包含小写字母</el-checkbox>
                <el-checkbox label="numbers">包含数字</el-checkbox>
                <el-checkbox label="symbols">包含特殊字符</el-checkbox>
              </el-checkbox-group>
            </el-form-item>
            
            <el-form-item label="会话超时时间">
              <el-input-number
                v-model="securitySettings.session_timeout"
                :min="30"
                :max="1440"
                style="width: 200px"
              />
              <span style="margin-left: 10px">分钟</span>
            </el-form-item>
            
            <el-form-item label="登录失败锁定">
              <el-switch
                v-model="securitySettings.login_lock_enabled"
                active-text="开启"
                inactive-text="关闭"
              />
            </el-form-item>
            
            <el-form-item v-if="securitySettings.login_lock_enabled" label="最大失败次数">
              <el-input-number
                v-model="securitySettings.max_login_attempts"
                :min="3"
                :max="10"
                style="width: 200px"
              />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="saveSecuritySettings" :loading="saving">
                保存设置
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
        
        <!-- 备份设置 -->
        <el-card v-show="activeMenu === 'backup'" class="settings-content">
          <template #header>
            <span>备份设置</span>
          </template>
          
          <el-form :model="backupSettings" label-width="150px">
            <el-form-item label="自动备份">
              <el-switch
                v-model="backupSettings.auto_backup_enabled"
                active-text="开启"
                inactive-text="关闭"
              />
            </el-form-item>
            
            <el-form-item v-if="backupSettings.auto_backup_enabled" label="备份频率">
              <el-select v-model="backupSettings.backup_frequency">
                <el-option label="每日" value="daily" />
                <el-option label="每周" value="weekly" />
                <el-option label="每月" value="monthly" />
              </el-select>
            </el-form-item>
            
            <el-form-item v-if="backupSettings.auto_backup_enabled" label="备份时间">
              <el-time-picker
                v-model="backupSettings.backup_time"
                format="HH:mm"
                value-format="HH:mm"
                placeholder="选择备份时间"
              />
            </el-form-item>
            
            <el-form-item label="保留备份数量">
              <el-input-number
                v-model="backupSettings.backup_retention_count"
                :min="1"
                :max="30"
                style="width: 200px"
              />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="saveBackupSettings" :loading="saving">
                保存设置
              </el-button>
              <el-button type="success" @click="createBackup" :loading="backing">
                立即备份
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
        
        <!-- 系统信息 -->
        <el-card v-show="activeMenu === 'system'" class="settings-content">
          <template #header>
            <span>系统信息</span>
          </template>
          
          <el-descriptions :column="2" border>
            <el-descriptions-item label="系统版本">
              {{ systemInfo.version }}
            </el-descriptions-item>
            <el-descriptions-item label="数据库版本">
              {{ systemInfo.database_version }}
            </el-descriptions-item>
            <el-descriptions-item label="运行时间">
              {{ systemInfo.uptime }}
            </el-descriptions-item>
            <el-descriptions-item label="CPU使用率">
              {{ systemInfo.cpu_usage }}%
            </el-descriptions-item>
            <el-descriptions-item label="内存使用率">
              {{ systemInfo.memory_usage }}%
            </el-descriptions-item>
            <el-descriptions-item label="磁盘使用率">
              {{ systemInfo.disk_usage }}%
            </el-descriptions-item>
            <el-descriptions-item label="最后备份时间">
              {{ systemInfo.last_backup_time }}
            </el-descriptions-item>
            <el-descriptions-item label="在线用户数">
              {{ systemInfo.online_users }}
            </el-descriptions-item>
          </el-descriptions>
          
          <div style="margin-top: 20px;">
            <el-button @click="refreshSystemInfo" :loading="refreshing">
              刷新信息
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Setting, Bell, Lock, Download, Monitor } from '@element-plus/icons-vue'

const basicFormRef = ref()
const activeMenu = ref('basic')
const saving = ref(false)
const backing = ref(false)
const refreshing = ref(false)

const basicSettings = reactive({
  system_name: '实验室管理系统',
  system_description: '高效的实验室资源管理平台',
  default_reservation_duration: 2,
  advance_booking_hours: 24,
  auto_approval: false
})

const notificationSettings = reactive({
  email_enabled: true,
  smtp_server: 'smtp.example.com',
  smtp_port: 587,
  reservation_reminder: true,
  maintenance_reminder: true
})

const securitySettings = reactive({
  min_password_length: 8,
  password_requirements: ['lowercase', 'numbers'],
  session_timeout: 120,
  login_lock_enabled: true,
  max_login_attempts: 5
})

const backupSettings = reactive({
  auto_backup_enabled: true,
  backup_frequency: 'daily',
  backup_time: '02:00',
  backup_retention_count: 7
})

const systemInfo = reactive({
  version: '1.0.0',
  database_version: 'MySQL 8.0.25',
  uptime: '15天 8小时 32分钟',
  cpu_usage: 25.6,
  memory_usage: 68.3,
  disk_usage: 45.2,
  last_backup_time: '2024-01-15 02:00:00',
  online_users: 12
})

const basicRules = {
  system_name: [
    { required: true, message: '请输入系统名称', trigger: 'blur' }
  ],
  default_reservation_duration: [
    { required: true, message: '请输入默认预约时长', trigger: 'blur' }
  ],
  advance_booking_hours: [
    { required: true, message: '请输入预约提前时间', trigger: 'blur' }
  ]
}

const handleMenuSelect = (index) => {
  activeMenu.value = index
}

const saveBasicSettings = async () => {
  try {
    await basicFormRef.value.validate()
    saving.value = true
    
    // TODO: 调用API保存基本设置
    // await api.saveBasicSettings(basicSettings)
    
    ElMessage.success('基本设置保存成功')
  } catch (error) {
    if (error !== false) {
      ElMessage.error('保存失败，请重试')
    }
  } finally {
    saving.value = false
  }
}

const saveNotificationSettings = async () => {
  try {
    saving.value = true
    
    // TODO: 调用API保存通知设置
    // await api.saveNotificationSettings(notificationSettings)
    
    ElMessage.success('通知设置保存成功')
  } catch (error) {
    ElMessage.error('保存失败，请重试')
  } finally {
    saving.value = false
  }
}

const saveSecuritySettings = async () => {
  try {
    saving.value = true
    
    // TODO: 调用API保存安全设置
    // await api.saveSecuritySettings(securitySettings)
    
    ElMessage.success('安全设置保存成功')
  } catch (error) {
    ElMessage.error('保存失败，请重试')
  } finally {
    saving.value = false
  }
}

const saveBackupSettings = async () => {
  try {
    saving.value = true
    
    // TODO: 调用API保存备份设置
    // await api.saveBackupSettings(backupSettings)
    
    ElMessage.success('备份设置保存成功')
  } catch (error) {
    ElMessage.error('保存失败，请重试')
  } finally {
    saving.value = false
  }
}

const createBackup = async () => {
  try {
    backing.value = true
    
    // TODO: 调用API创建备份
    // await api.createBackup()
    
    ElMessage.success('备份创建成功')
  } catch (error) {
    ElMessage.error('备份失败，请重试')
  } finally {
    backing.value = false
  }
}

const refreshSystemInfo = async () => {
  try {
    refreshing.value = true
    
    // TODO: 调用API获取系统信息
    // const response = await api.getSystemInfo()
    // Object.assign(systemInfo, response.data)
    
    ElMessage.success('系统信息已刷新')
  } catch (error) {
    ElMessage.error('刷新失败，请重试')
  } finally {
    refreshing.value = false
  }
}

const loadSettings = async () => {
  try {
    // TODO: 调用API加载所有设置
    // const response = await api.getSettings()
    // Object.assign(basicSettings, response.data.basic)
    // Object.assign(notificationSettings, response.data.notification)
    // Object.assign(securitySettings, response.data.security)
    // Object.assign(backupSettings, response.data.backup)
  } catch (error) {
    console.error('加载设置失败:', error)
  }
}

onMounted(() => {
  loadSettings()
})
</script>

<style scoped>
.settings-index {
  padding: 20px;
}

.settings-menu {
  height: fit-content;
}

.settings-menu-list {
  border: none;
}

.settings-content {
  min-height: 500px;
}
</style>