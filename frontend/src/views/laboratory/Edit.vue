<template>
  <div class="laboratory-edit">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>编辑实验室</span>
        </div>
      </template>
      
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
        class="laboratory-form"
        v-loading="pageLoading"
      >
        <el-form-item label="实验室名称" prop="lab_name">
          <el-input
            v-model="form.lab_name"
            placeholder="请输入实验室名称"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="位置" prop="location">
          <el-input
            v-model="form.location"
            placeholder="请输入实验室位置"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="容量" prop="capacity">
          <el-input-number
            v-model="form.capacity"
            :min="1"
            :max="999"
            placeholder="请输入容量"
          />
        </el-form-item>
        
        <el-form-item label="状态" prop="lab_status">
          <el-select v-model="form.lab_status" placeholder="请选择状态">
            <el-option label="可用" value="可用" />
            <el-option label="维护中" value="维护中" />
            <el-option label="停用" value="停用" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="负责人" prop="manager_id">
          <el-select
            v-model="form.manager_id"
            placeholder="请选择负责人"
            filterable
            remote
            :remote-method="searchUsers"
            :loading="userLoading"
          >
            <el-option
              v-for="user in users"
              :key="user.user_id"
              :label="user.name"
              :value="user.user_id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="loading">
            保存
          </el-button>
          <el-button @click="handleCancel">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()
const formRef = ref()
const loading = ref(false)
const pageLoading = ref(false)
const userLoading = ref(false)
const users = ref([])

const form = reactive({
  lab_id: null,
  lab_name: '',
  location: '',
  capacity: 1,
  lab_status: '可用',
  manager_id: null
})

const rules = {
  lab_name: [
    { required: true, message: '请输入实验室名称', trigger: 'blur' },
    { min: 2, max: 100, message: '长度在 2 到 100 个字符', trigger: 'blur' }
  ],
  location: [
    { required: true, message: '请输入实验室位置', trigger: 'blur' },
    { max: 200, message: '长度不能超过 200 个字符', trigger: 'blur' }
  ],
  capacity: [
    { required: true, message: '请输入容量', trigger: 'blur' },
    { type: 'number', min: 1, message: '容量必须大于0', trigger: 'blur' }
  ],
  lab_status: [
    { required: true, message: '请选择状态', trigger: 'change' }
  ]
}

const loadLaboratory = async () => {
  const id = route.params.id
  if (!id) {
    ElMessage.error('实验室ID不存在')
    router.back()
    return
  }
  
  pageLoading.value = true
  try {
    // TODO: 调用API获取实验室详情
    // const response = await api.getLaboratory(id)
    // Object.assign(form, response.data)
    
    // 模拟数据
    Object.assign(form, {
      lab_id: id,
      lab_name: '物理实验室A',
      location: '教学楼3楼301',
      capacity: 30,
      lab_status: '可用',
      manager_id: 1
    })
    
    // 加载当前负责人信息
    users.value = [
      { user_id: 1, name: '张老师' }
    ]
  } catch (error) {
    ElMessage.error('加载实验室信息失败')
    router.back()
  } finally {
    pageLoading.value = false
  }
}

const searchUsers = async (query) => {
  if (query) {
    userLoading.value = true
    try {
      // TODO: 调用API搜索用户
      // const response = await api.searchUsers(query)
      // users.value = response.data
      
      // 模拟数据
      users.value = [
        { user_id: 1, name: '张老师' },
        { user_id: 2, name: '李老师' },
        { user_id: 3, name: '王老师' }
      ]
    } catch (error) {
      ElMessage.error('搜索用户失败')
    } finally {
      userLoading.value = false
    }
  }
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    loading.value = true
    
    // TODO: 调用API更新实验室
    // await api.updateLaboratory(form.lab_id, form)
    
    ElMessage.success('实验室更新成功')
    router.push('/laboratory/list')
  } catch (error) {
    if (error !== false) {
      ElMessage.error('更新失败，请重试')
    }
  } finally {
    loading.value = false
  }
}

const handleCancel = () => {
  router.back()
}

onMounted(() => {
  loadLaboratory()
})
</script>

<style scoped>
.laboratory-edit {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.laboratory-form {
  max-width: 600px;
}
</style>