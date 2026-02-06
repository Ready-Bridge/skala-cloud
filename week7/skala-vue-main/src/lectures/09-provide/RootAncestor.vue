<template>
  <div>
    <h2>Root Provider</h2>
    <label>메시지(provide):</label>
    <input v-model="message" placeholder="메시지를 입력하세요" />
    <MiddleParent />
  </div>
</template>

<script setup>
import { provide, ref } from 'vue'
import MiddleParent from './MiddleParent.vue'

const message = ref('')

provide('message', message)
</script>

<style scoped>
input {
  padding: 8px;
  margin: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  width: 300px;
}
</style>
