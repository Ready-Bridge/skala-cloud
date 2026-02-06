<template>
  <div class="middle-container">
    <h2>Middle Parent</h2>
    <div><b>메시지(inject):</b> {{ message }}</div>
    <DeepChild />
  </div>
</template>

<script setup>
import { inject } from 'vue'
import DeepChild from './DeepChild.vue'

const message = inject('message')
const count = inject('count')

console.log('MiddleParent - injected message:', message)
console.log('MiddleParent - injected count:', count)
</script>

<style scoped>
h2 {
  color: blue;
}

div {
  margin-bottom: 10px;
}

.middle-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  font-family: Arial, sans-serif;
  border: 2px solid blue;
}
</style>