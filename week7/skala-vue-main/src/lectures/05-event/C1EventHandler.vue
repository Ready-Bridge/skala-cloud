<template>
  <div>
    <button @click="count++">클릭(직접처리)</button>
    <button @click="handleClick">클릭(핸들러호출)</button>
  </div>
  <div style="margin: 4px;">
    카운트: {{ count }}
  </div>
</template>

<script setup>
import { ref } from 'vue'

const count = ref(0)

function handleClick() {
  count.value++
}

</script>

<style scoped>
button {
  margin: 4px;
  padding: 8px 16px;
  font-size: 16px;
}
</style>