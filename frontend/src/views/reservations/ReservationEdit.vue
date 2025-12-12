<template>
  <div class="reservation-edit-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>编辑预约</span>
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

        <el-form-item label="所需设备" prop="equipmentIds">
          <el-select
            v-model="reservationForm.equipmentIds"
            multiple
            placeholder="请选择所需设备（可选）"
            style="width: 100%"
            collapse-tags
            collapse-tags-tooltip
          >
            <el-option
              v-for="item in equipmentOptions"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            >
              <span>{{ item.name }}</span>
              <span style="float: right; color: #8492a6; font-size: 13px">
                {{ item.model }}
              </span>
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="课程" prop="courseId">
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

        <el-alert
          v-if="conflictCheckResult"
          :title="conflictCheckResult.hasConflict ? '时间冲突' : '时间可用'"
          :type="conflictCheckResult.hasConflict ? 'error' : 'success'"
          :description="conflictCheckResult.message"
          show-icon
          :closable="false"
          class="conflict-alert"
        />

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
            {{ submitLoading ? '保存中...' : '保存修改' }}
          </el-button>
          <el-button @click="goBack">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import {
  getReservationByIdApi,
  updateReservationApi,
  checkReservationConflictApi
} from '@/api/reservation'
import { getLabsApi } from '@/api/lab'

const route = useRoute()
const router = useRouter()

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
  equipmentIds: [],
  expectedPeople: 1,
  remarks: ''
})

const equipmentOptions = computed(() => {
  if (!selectedLab.value || !selectedLab.value.equipment) return []
  return selectedLab.value.equipment
})

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

const disabledDate = (date) => {
  return dayjs(date).isBefore(dayjs().startOf('day'))
}

const disabledHours = () => []
const disabledMinutes = () => []

const handleLabChange = (val) => {
  const lab = labOptions.value.find(l => l.id === val)
  selectedLab.value = lab || null
}

const handleDateChange = () => checkConflict()
const handleTimeChange = () => checkConflict()

const checkConflict = async () => {
  if (!reservationForm.labId || !reservationForm.reservationDate || !reservationForm.startTime || !reservationForm.endTime) {
    conflictCheckResult.value = null
    return
  }

  try {
    const startDateTime = `${reservationForm.reservationDate} ${reservationForm.startTime}:00`
    const endDateTime = `${reservationForm.reservationDate} ${reservationForm.endTime}:00`

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
    console.error('检查冲突失败:', error)
  }
}

const handleSubmit = async () => {
  try {
    await reservationFormRef.value.validate()
    submitLoading.value = true

    const submitData = {
      laboratory_id: reservationForm.labId,
      reservation_date: reservationForm.reservationDate,
      start_time: reservationForm.startTime,
      end_time: reservationForm.endTime,
      purpose: reservationForm.purpose,
      participant_count: reservationForm.expectedPeople,
      remarks: reservationForm.remarks,
      equipment_ids: reservationForm.equipmentIds
    }

    if (reservationForm.courseId) {
      submitData.course_id = reservationForm.courseId
    }

    const id = route.params.id
    const response = await updateReservationApi(id, submitData)

    if (response.code === 200) {
      ElMessage.success('预约更新成功')
      router.push('/reservation/list')
    }
  } catch (error) {
    console.error('更新预约失败:', error)
  } finally {
    submitLoading.value = false
  }
}

const goBack = () => {
  router.go(-1)
}

const loadLabs = async () => {
  try {
    const response = await getLabsApi({ page: 1, page_size: 100 })
    if (response.code === 200) {
      labOptions.value = response.data.list || response.data
    }
  } catch (error) {
    console.error('加载实验室失败:', error)
  }
}

const loadDetail = async () => {
  try {
    const id = route.params.id
    const response = await getReservationByIdApi(id)
    if (response.code === 200) {
      const d = response.data
      reservationForm.labId = d.lab_id
      reservationForm.reservationDate = dayjs(d.start_time).format('YYYY-MM-DD')
      reservationForm.startTime = dayjs(d.start_time).format('HH:mm')
      reservationForm.endTime = dayjs(d.end_time).format('HH:mm')
      reservationForm.purpose = d.purpose
      reservationForm.expectedPeople = d.expected_people
      reservationForm.remarks = d.remarks || ''
      reservationForm.courseId = d.course_id || ''
      // Map equipment objects to IDs if present
      reservationForm.equipmentIds = d.equipment ? d.equipment.map(e => e.id) : []
      handleLabChange(reservationForm.labId)
    }
  } catch (error) {
    console.error('加载预约详情失败:', error)
  }
}

onMounted(() => {
  loadLabs()
  loadDetail()
})
</script>

<style scoped>
.reservation-edit-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.reservation-form {
  max-width: 800px;
}

.conflict-alert {
  margin-bottom: 20px;
}

.lab-info {
  margin: 20px 0;
}

.equipment-tag {
  margin-right: 8px;
  margin-bottom: 6px;
}
</style>