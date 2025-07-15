<template>
  <div v-if="hasAccess">
    <slot></slot>
  </div>
  <div v-else-if="showFallback" class="permission-denied">
    <el-empty 
      description="权限不足"
      :image-size="100">
      <template #description>
        <p>{{ fallbackMessage || '您没有权限执行此操作' }}</p>
      </template>
    </el-empty>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useUserStore } from '@/utils/userStore'

const props = defineProps({
  permission: {
    type: String,
    default: 'view'
  },
  adminOnly: {
    type: Boolean,
    default: false
  },
  showFallback: {
    type: Boolean,
    default: false
  },
  fallbackMessage: {
    type: String,
    default: ''
  }
})

const userStore = useUserStore()

const hasAccess = computed(() => {
  if (props.adminOnly) {
    return userStore.isAdmin()
  }
  
  return userStore.canPerform(props.permission)
})
</script>

<style scoped>
.permission-denied {
  padding: 40px;
  text-align: center;
}
</style> 