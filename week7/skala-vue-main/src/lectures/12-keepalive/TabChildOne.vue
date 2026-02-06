<template>
  <div>
    <h3>첫번째 탭</h3>
    <label>이름: </label>
    <input v-model="text" placeholder="이름을 입력하세요" />
    <p>입력값: {{ text }}</p>
    <div>
      <h4>라이프사이클 이벤트</h4>
      <ul>
        <li v-for="(event, index) in events" :key="index">{{ event }}</li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onActivated, onDeactivated } from 'vue'

const events = ref([])

const text = ref('')
onMounted(() => {
  events.value.push('Mounted')
})
onActivated(() => {
  events.value.push('Activated')
})
onDeactivated(() => {
  events.value.push('Deactivated')
})
</script>
