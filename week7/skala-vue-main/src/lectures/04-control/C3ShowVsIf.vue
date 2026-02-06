<template>
  <button @click="toggle">Toggle View</button>
  <div v-if="visible">👀 v-if로 렌더링된 박스</div>
  <div v-show="visible">🙈 v-show로 렌더링된 박스</div>
</template>

<script setup>
import { ref } from 'vue'

const visible = ref(true)

function toggle() {
  visible.value = !visible.value
}
</script>

<style scoped>
div {
  margin-top: 10px;
  padding: 10px;
  border: 1px solid gray;
}
</style>
