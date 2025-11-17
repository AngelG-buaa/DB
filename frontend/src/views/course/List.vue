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
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

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
    
    // TODO: 调用API获取课程列表
    // const response = await api.getCourses({
    //   page: pagination.page,
    //   size: pagination.size,
    //   ...searchForm
    // })
    // courseList.value = response.data.list
    // pagination.total = response.data.total
    
    // 模拟数据
    courseList.value = [
      {
        course_id: 1,
        course_name: '大学物理实验',
        teacher_name: '张教授',
        teacher_id: 1,
        credit: 2,
        need_lab: true,
        lab_name: '物理实验室A'
      },
      {
        course_id: 2,
        course_name: '有机化学实验',
        teacher_name: '李教授',
        teacher_id: 2,
        credit: 3,
        need_lab: true,
        lab_name: '化学实验室B'
      },
      {
        course_id: 3,
        course_name: '计算机基础',
        teacher_name: '王老师',
        teacher_id: 3,
        credit: 2,
        need_lab: false,
        lab_name: null
      }
    ]
    pagination.total = 3
  } catch (error) {
    ElMessage.error('加载课程列表失败')
  } finally {
    loading.value = false
  }
}

const loadTeachers = async () => {
  try {
    // TODO: 调用API获取教师列表
    // const response = await api.getTeachers()
    // teachers.value = response.data
    
    // 模拟数据
    teachers.value = [
      { user_id: 1, user_name: '张教授' },
      { user_id: 2, user_name: '李教授' },
      { user_id: 3, user_name: '王老师' }
    ]
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
  router.push(`/course/edit/${row.course_id}`)
}

const handleViewStudents = (row) => {
  router.push(`/course/${row.course_id}/students`)
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
    
    // TODO: 调用API删除课程
    // await api.deleteCourse(row.course_id)
    
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