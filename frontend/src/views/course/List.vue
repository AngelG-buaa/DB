<template>
  <div class="course-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>课程管理</span>
          <el-button type="primary" @click="handleCreate">
            <el-icon><Plus /></el-icon>
            新增课程
          </el-button>
        </div>
      </template>
      
      <!-- 搜索区域 -->
      <div class="search-area">
        <el-form :model="searchForm" inline>
          <el-form-item label="课程名称">
            <el-input
              v-model="searchForm.course_name"
              placeholder="请输入课程名称"
              clearable
              style="width: 200px"
            />
          </el-form-item>
          <el-form-item label="授课教师">
            <el-select
              v-model="searchForm.teacher_id"
              placeholder="请选择教师"
              clearable
              filterable
            >
              <el-option
                v-for="teacher in teachers"
                :key="teacher.user_id"
                :label="teacher.user_name"
                :value="teacher.user_id"
              />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">搜索</el-button>
            <el-button @click="handleReset">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
      
      <!-- 课程表格 -->
      <el-table
        :data="courseList"
        v-loading="loading"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="course_id" label="课程ID" width="80" />
        <el-table-column prop="course_name" label="课程名称" min-width="150" />
        <el-table-column prop="teacher_name" label="授课教师" width="120" />
        <el-table-column prop="credit" label="学分" width="80" />
        <el-table-column prop="need_lab" label="需要实验室" width="100">
          <template #default="{ row }">
            <el-tag :type="row.need_lab ? 'success' : 'info'">
              {{ row.need_lab ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="lab_name" label="关联实验室" min-width="120" />
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
              @click="handleViewStudents(row)"
            >
              学生列表
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
    <el-dialog v-model="studentsDialogVisible" title="学生列表" width="600px">
      <div v-if="currentCourseStudents.length === 0">暂无学生数据</div>
      <el-table v-else :data="currentCourseStudents" stripe>
        <el-table-column prop="id" label="学生ID" width="120" />
        <el-table-column prop="name" label="姓名" />
      </el-table>
      <template #footer>
        <el-button @click="studentsDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getCoursesApi, deleteCourseApi } from '@/api/course'
import { getUsersApi } from '@/api/user'

const router = useRouter()
const loading = ref(false)
const courseList = ref([])
const teachers = ref([])

const searchForm = reactive({
  course_name: '',
  teacher_id: null
})

const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

const loadCourses = async () => {
  try {
    loading.value = true
    const params = {
      page: pagination.page,
      page_size: pagination.size,
      search: searchForm.course_name || undefined,
      teacher_id: searchForm.teacher_id || undefined
    }
  const response = await getCoursesApi(params)
  if (response.code === 200) {
      courseList.value = (response.data.list || []).map(c => ({
          course_id: c.id,
          course_name: c.name,
          teacher_name: c.teacher?.name || '',
          credit: c.credits,
          need_lab: (typeof c.requires_lab === 'undefined' ? !!c.laboratory_id : !!c.requires_lab),
          lab_name: c.laboratory_name || ''
      }))
      pagination.total = response.data.total || 0
  }
  } catch (error) {
    ElMessage.error('加载课程列表失败')
  } finally {
    loading.value = false
  }
}

const loadTeachers = async () => {
  try {
    const response = await getUsersApi({ page: 1, page_size: 100, role: 'teacher' })
    if (response.code === 200) {
      teachers.value = (response.data.list || []).map(u => ({ user_id: u.id, user_name: u.name || u.username }))
    }
  } catch (error) {
    ElMessage.error('加载教师列表失败')
  }
}

const handleSearch = () => {
  pagination.page = 1
  loadCourses()
}

const handleReset = () => {
  Object.assign(searchForm, {
    course_name: '',
    teacher_id: null
  })
  pagination.page = 1
  loadCourses()
}

const handleCreate = () => {
  router.push('/course/create')
}

const handleEdit = (row) => {
  router.push({ path: '/course/create', query: { edit: row.course_id } })
}

const studentsDialogVisible = ref(false)
const currentCourseStudents = ref([])

const handleViewStudents = async (row) => {
  try {
    // 目前后端未提供课程学生列表接口，这里展示占位信息避免404
    currentCourseStudents.value = []
    studentsDialogVisible.value = true
  } catch (error) {
    ElMessage.error('加载学生列表失败')
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除课程"${row.course_name}"吗？`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await deleteCourseApi(row.course_id)
    
    ElMessage.success('删除成功')
    loadCourses()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleSizeChange = (size) => {
  pagination.size = size
  pagination.page = 1
  loadCourses()
}

const handleCurrentChange = (page) => {
  pagination.page = page
  loadCourses()
}

onMounted(() => {
  loadCourses()
  loadTeachers()
})
</script>

<style scoped>
.course-list {
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