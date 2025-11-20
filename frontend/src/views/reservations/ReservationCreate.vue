<template>
  <div class="reservation-create-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>新建预约</span>
          <el-button @click="goBack">
            <el-icon><ArrowLeft /></el-icon>
            返回
          </el-button>
        </div>
      </template>
      
      <el-form
        ref="reservationFormRef"
        :model="reservationForm"
        :rules="reservationRules"
        label-width="120px"
        class="reservation-form"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="实验室" prop="labId">
              <el-select
                v-model="reservationForm.labId"
                placeholder="请选择实验室"
                style="width: 100%"
                @change="handleLabChange"
              >
                <el-option
                  v-for="lab in labOptions"
                  :key="lab.id"
                  :label="lab.name"
                  :value="lab.id"
                >
                  <span>{{ lab.name }}</span>
                  <span style="float: right; color: #8492a6; font-size: 13px">
                    容量: {{ lab.capacity }}人
                  </span>
                </el-option>
              </el-select>
            </el-form-item>
          </el-col>
          
          <el-col :span="12">
            <el-form-item label="预约日期" prop="reservationDate">
              <el-date-picker
                v-model="reservationForm.reservationDate"
                type="date"
                placeholder="请选择预约日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                :disabled-date="disabledDate"
                style="width: 100%"
                @change="handleDateChange"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="开始时间" prop="startTime">
              <el-time-picker
                v-model="reservationForm.startTime"
                placeholder="请选择开始时间"
                format="HH:mm"
                value-format="HH:mm"
                :disabled-hours="disabledHours"
                :disabled-minutes="disabledMinutes"
                style="width: 100%"
                @change="handleTimeChange"
              />
            </el-form-item>
          </el-col>
          
          <el-col :span="12">
            <el-form-item label="结束时间" prop="endTime">
              <el-time-picker
                v-model="reservationForm.endTime"
                placeholder="请选择结束时间"
                format="HH:mm"
                value-format="HH:mm"
                :disabled-hours="disabledHours"
                :disabled-minutes="disabledMinutes"
                style="width: 100%"
                @change="handleTimeChange"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="使用目的" prop="purpose">
          <el-input
            v-model="reservationForm.purpose"
            placeholder="请输入使用目的"
            clearable
          />
        </el-form-item>
        
        <el-form-item label="课程" prop="courseId" v-if="userInfo.user_type === 'teacher'">
          <el-select
            v-model="reservationForm.courseId"
            placeholder="请选择课程（可选）"
            clearable
            style="width: 100%"
          >
            <el-option
              v-for="course in courseOptions"
              :key="course.id"
              :label="course.name"
              :value="course.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="预计人数" prop="expectedPeople">
          <el-input-number
            v-model="reservationForm.expectedPeople"
            :min="1"
            :max="selectedLab?.capacity || 100"
            placeholder="请输入预计使用人数"
            style="width: 100%"
          />
        </el-form-item>
        
        <el-form-item label="备注">
          <el-input
            v-model="reservationForm.remarks"
            type="textarea"
            :rows="4"
            placeholder="请输入备注信息（可选）"
          />
        </el-form-item>
        
        <!-- 时间冲突检查结果 -->
        <el-alert
          v-if="conflictCheckResult"
          :title="conflictCheckResult.hasConflict ? '时间冲突' : '时间可用'"
          :type="conflictCheckResult.hasConflict ? 'error' : 'success'"
          :description="conflictCheckResult.message"
          show-icon
          :closable="false"
          class="conflict-alert"
        />
        
        <!-- 实验室信息 -->
        <div v-if="selectedLab" class="lab-info">
          <h4>实验室信息</h4>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="实验室名称">
              {{ selectedLab.name }}
            </el-descriptions-item>
            <el-descriptions-item label="容量">
              {{ selectedLab.capacity }}人
            </el-descriptions-item>
            <el-descriptions-item label="位置">
              {{ selectedLab.location }}
            </el-descriptions-item>
            <el-descriptions-item label="负责人">
              {{ selectedLab.manager }}
            </el-descriptions-item>
            <el-descriptions-item label="设备" :span="2">
              <el-tag
                v-for="equipment in selectedLab.equipment"
                :key="equipment.id"
                class="equipment-tag"
              >
                {{ equipment.name }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="描述" :span="2">
              {{ selectedLab.description || '无' }}
            </el-descriptions-item>
          </el-descriptions>
        </div>
        
        <el-form-item>
          <el-button
            type="primary"
            :loading="submitLoading"
            :disabled="conflictCheckResult?.hasConflict"
            @click="handleSubmit"
          >
            {{ submitLoading ? '提交中...' : '提交预约' }}
          </el-button>
          <el-button @click="handleReset">重置</el-button>
          <el-button @click="goBack">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import { useUserStore } from '@/stores/user'
import {
  createReservationApi,
  checkReservationConflictApi
} from '@/api/reservation'
import { getLabsApi, getLabByIdApi } from '@/api/lab'
import { getCoursesApi } from '@/api/course'

const router = useRouter()
const userStore = useUserStore()

// 响应式数据
const reservationFormRef = ref()
const submitLoading = ref(false)
const labOptions = ref([])
const courseOptions = ref([])
const selectedLab = ref(null)
const conflictCheckResult = ref(null)

const reservationForm = reactive({
  labId: '',
  reservationDate: '',
  startTime: '',
  endTime: '',
  purpose: '',
  courseId: '',
  expectedPeople: 1,
  remarks: ''
})

// 计算属性
const userInfo = computed(() => userStore.userInfo)

// 表单验证规则
const reservationRules = {
  labId: [
    { required: true, message: '请选择实验室', trigger: 'change' }
  ],
  reservationDate: [
    { required: true, message: '请选择预约日期', trigger: 'change' }
  ],
  startTime: [
    { required: true, message: '请选择开始时间', trigger: 'change' }
  ],
  endTime: [
    { required: true, message: '请选择结束时间', trigger: 'change' }
  ],
  purpose: [
    { required: true, message: '请输入使用目的', trigger: 'blur' },
    { min: 5, max: 200, message: '使用目的长度在 5 到 200 个字符', trigger: 'blur' }
  ],
  expectedPeople: [
    { required: true, message: '请输入预计使用人数', trigger: 'blur' }
  ]
}

// 监听器
watch(
  () => [reservationForm.labId, reservationForm.reservationDate, reservationForm.startTime, reservationForm.endTime],
  () => {
    if (reservationForm.labId && reservationForm.reservationDate && reservationForm.startTime && reservationForm.endTime) {
      checkTimeConflict()
    } else {
      conflictCheckResult.value = null
    }
  },
  { deep: true }
)

// 方法
const loadLabOptions = async () => {
  try {
    const response = await getLabsApi({ page: 1, page_size: 100 })
    if (response.code === 200) {
      labOptions.value = response.data.list
    }
  } catch (error) {
    console.error('加载实验室选项失败:', error)
  }
}

const loadCourseOptions = async () => {
  if (userInfo.value.user_type !== 'teacher') return
  
  try {
    const response = await getCoursesApi({ 
      page: 1, 
      page_size: 100,
      teacher_id: userInfo.value.id
    })
    if (response.code === 200) {
      courseOptions.value = response.data.list
    }
  } catch (error) {
    console.error('加载课程选项失败:', error)
  }
}

const handleLabChange = async (labId) => {
  if (!labId) {
    selectedLab.value = null
    return
  }
  
  try {
    const response = await getLabByIdApi(labId)
    if (response.code === 200) {
      selectedLab.value = response.data
      // 重置预计人数的最大值
      if (reservationForm.expectedPeople > selectedLab.value.capacity) {
        reservationForm.expectedPeople = selectedLab.value.capacity
      }
    }
  } catch (error) {
    console.error('获取实验室详情失败:', error)
  }
}

const handleDateChange = () => {
  // 日期改变时重新检查时间冲突
  conflictCheckResult.value = null
}

const handleTimeChange = () => {
  // 时间改变时重新检查时间冲突
  conflictCheckResult.value = null
}

const checkTimeConflict = async () => {
  try {
    const startDateTime = `${reservationForm.reservationDate} ${reservationForm.startTime}:00`
    const endDateTime = `${reservationForm.reservationDate} ${reservationForm.endTime}:00`
    
    // 检查时间逻辑
    if (reservationForm.startTime >= reservationForm.endTime) {
      conflictCheckResult.value = {
        hasConflict: true,
        message: '结束时间必须晚于开始时间'
      }
      return
    }
    
    const response = await checkReservationConflictApi({
      laboratory_id: reservationForm.labId,
      date: reservationForm.reservationDate,
      start_time: reservationForm.startTime,
      end_time: reservationForm.endTime
    })
    
    if (response.code === 200) {
      conflictCheckResult.value = response.data
    }
  } catch (error) {
    console.error('检查时间冲突失败:', error)
  }
}

const disabledDate = (time) => {
  // 不能选择今天之前的日期
  return time.getTime() < Date.now() - 8.64e7
}

const disabledHours = () => {
  // 实验室开放时间：8:00-22:00
  const hours = []
  for (let i = 0; i < 8; i++) {
    hours.push(i)
  }
  for (let i = 22; i < 24; i++) {
    hours.push(i)
  }
  return hours
}

const disabledMinutes = (hour) => {
  // 只允许整点和半点
  const minutes = []
  for (let i = 0; i < 60; i++) {
    if (i !== 0 && i !== 30) {
      minutes.push(i)
    }
  }
  return minutes
}

const handleSubmit = async () => {
  if (!reservationFormRef.value) return
  
  try {
    await reservationFormRef.value.validate()
    
    if (conflictCheckResult.value?.hasConflict) {
      ElMessage.error('存在时间冲突，请重新选择时间')
      return
    }
    
    submitLoading.value = true
    
    const startDateTime = `${reservationForm.reservationDate} ${reservationForm.startTime}:00`
    const endDateTime = `${reservationForm.reservationDate} ${reservationForm.endTime}:00`
    
    const submitData = {
      laboratory_id: reservationForm.labId,
      reservation_date: reservationForm.reservationDate,
      start_time: reservationForm.startTime,
      end_time: reservationForm.endTime,
      purpose: reservationForm.purpose,
      participant_count: reservationForm.expectedPeople,
      remarks: reservationForm.remarks
    }
    
    if (reservationForm.courseId) {
      submitData.course_id = reservationForm.courseId
    }
    
    const response = await createReservationApi(submitData)
    
    if (response.code === 200) {
      ElMessage.success('预约提交成功，请等待审核')
      router.push('/reservation/list')
    }
  } catch (error) {
    console.error('提交预约失败:', error)
  } finally {
    submitLoading.value = false
  }
}

const handleReset = () => {
  reservationForm.labId = ''
  reservationForm.reservationDate = ''
  reservationForm.startTime = ''
  reservationForm.endTime = ''
  reservationForm.purpose = ''
  reservationForm.courseId = ''
  reservationForm.expectedPeople = 1
  reservationForm.remarks = ''
  selectedLab.value = null
  conflictCheckResult.value = null
  
  if (reservationFormRef.value) {
    reservationFormRef.value.clearValidate()
  }
}

const goBack = () => {
  router.go(-1)
}

// 生命周期
onMounted(() => {
  loadLabOptions()
  loadCourseOptions()
})
</script>

<style lang="scss" scoped>
.reservation-create-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.reservation-form {
  max-width: 800px;
  
  .el-form-item {
    margin-bottom: 20px;
  }
}

.conflict-alert {
  margin-bottom: 20px;
}

.lab-info {
  margin: 20px 0;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  
  h4 {
    margin-bottom: 16px;
    color: #303133;
  }
  
  .equipment-tag {
    margin-right: 8px;
    margin-bottom: 4px;
  }
}

// 响应式设计
@media (max-width: 768px) {
  .reservation-create-container {
    padding: 10px;
  }
  
  .reservation-form {
    .el-col {
      margin-bottom: 10px;
    }
  }
  
  .card-header {
    flex-direction: column;
    gap: 10px;
    align-items: flex-start;
  }
}
</style>