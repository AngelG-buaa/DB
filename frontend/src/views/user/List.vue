<template>
  <div class="user-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>用户管理</span>
          <el-button type="primary" @click="handleCreate">
            <el-icon><Plus /></el-icon>
            新增用户
          </el-button>
        </div>
      </template>
      
      <!-- 搜索区域 -->
      <div class="search-area">
        <el-form :model="searchForm" inline>
          <el-form-item label="用户名">
            <el-input
              v-model="searchForm.user_name"
              placeholder="请输入用户名"
              clearable
              style="width: 200px"
            />
          </el-form-item>
          <el-form-item label="用户类型">
            <el-select
              v-model="searchForm.user_type"
              placeholder="请选择用户类型"
              clearable
            >
              <el-option label="学生" value="Student" />
              <el-option label="教师" value="Teacher" />
              <el-option label="管理员" value="Admin" />
            </el-select>
          </el-form-item>
          <el-form-item label="课程">
            <el-select
              v-model="searchForm.course_id"
              placeholder="请选择课程"
              clearable
              filterable
            >
              <el-option
                v-for="course in courses"
                :key="course.course_id"
                :label="course.course_name"
                :value="course.course_id"
              />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">搜索</el-button>
            <el-button @click="handleReset">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
      
      <!-- 用户表格 -->
      <el-table
        :data="userList"
        v-loading="loading"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="user_id" label="用户ID" width="80" />
        <el-table-column prop="user_name" label="用户名" min-width="120" />
        <el-table-column prop="user_type" label="用户类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getUserTypeColor(row.user_type)">
              {{ getUserTypeText(row.user_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="course_name" label="所属课程" min-width="150" />
        <el-table-column prop="major" label="专业" min-width="120" />
        <el-table-column prop="grade" label="年级" width="80" />
        <el-table-column prop="created_at" label="创建时间" width="160" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              @click="handleEdit(row)"
            >
              编辑
            </el-button>
            <el-button
              type="info"
              size="small"
              @click="handleViewReservations(row)"
            >
              预约记录
            </el-button>
            <el-button
              type="danger"
              size="small"
              @click="handleDelete(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

const router = useRouter()
const loading = ref(false)
const userList = ref([])
const courses = ref([])

const searchForm = reactive({
  user_name: '',
  user_type: '',
  course_id: null
})

const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

const getUserTypeColor = (type) => {
  const colorMap = {
    'Student': 'primary',
    'Teacher': 'success',
    'Admin': 'warning'
  }
  return colorMap[type] || 'info'
}

const getUserTypeText = (type) => {
  const textMap = {
    'Student': '学生',
    'Teacher': '教师',
    'Admin': '管理员'
  }
  return textMap[type] || type
}

const loadUsers = async () => {
  try {
    loading.value = true
    
    // TODO: 调用API获取用户列表
    // const response = await api.getUsers({
    //   page: pagination.page,
    //   size: pagination.size,
    //   ...searchForm
    // })
    // userList.value = response.data.list
    // pagination.total = response.data.total
    
    // 模拟数据
    userList.value = [
      {
        user_id: 1,
        user_name: '张三',
        user_type: 'Student',
        course_name: '大学物理实验',
        course_id: 1,
        major: '物理学',
        grade: '2023',
        created_at: '2023-09-01 10:00:00'
      },
      {
        user_id: 2,
        user_name: '李四',
        user_type: 'Student',
        course_name: '有机化学实验',
        course_id: 2,
        major: '化学',
        grade: '2022',
        created_at: '2023-09-01 10:30:00'
      },
      {
        user_id: 3,
        user_name: '王教授',
        user_type: 'Teacher',
        course_name: '大学物理实验',
        course_id: 1,
        major: '物理学院',
        grade: null,
        created_at: '2023-08-15 09:00:00'
      },
      {
        user_id: 4,
        user_name: '管理员',
        user_type: 'Admin',
        course_name: null,
        course_id: null,
        major: null,
        grade: null,
        created_at: '2023-08-01 08:00:00'
      }
    ]
    pagination.total = 4
  } catch (error) {
    ElMessage.error('加载用户列表失败')
  } finally {
    loading.value = false
  }
}

const loadCourses = async () => {
  try {
    // TODO: 调用API获取课程列表
    // const response = await api.getCourses()
    // courses.value = response.data
    
    // 模拟数据
    courses.value = [
      { course_id: 1, course_name: '大学物理实验' },
      { course_id: 2, course_name: '有机化学实验' },
      { course_id: 3, course_name: '生物学基础实验' }
    ]
  } catch (error) {
    ElMessage.error('加载课程列表失败')
  }
}

const handleSearch = () => {
  pagination.page = 1
  loadUsers()
}

const handleReset = () => {
  Object.assign(searchForm, {
    user_name: '',
    user_type: '',
    course_id: null
  })
  pagination.page = 1
  loadUsers()
}

const handleCreate = () => {
  router.push('/user/create')
}

const handleEdit = (row) => {
  router.push(`/user/edit/${row.user_id}`)
}

const handleViewReservations = (row) => {
  router.push(`/reservation/list?user_id=${row.user_id}`)
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除用户"${row.user_name}"吗？`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // TODO: 调用API删除用户
    // await api.deleteUser(row.user_id)
    
    ElMessage.success('删除成功')
    loadUsers()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleSizeChange = (size) => {
  pagination.size = size
  pagination.page = 1
  loadUsers()
}

const handleCurrentChange = (page) => {
  pagination.page = page
  loadUsers()
}

onMounted(() => {
  loadUsers()
  loadCourses()
})
</script>

<style scoped>
.user-list {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-area {
  margin-bottom: 20px;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.pagination {
  margin-top: 20px;
  text-align: right;
}
</style>