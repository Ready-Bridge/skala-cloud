<template>
  <div>
    <h2>watchEffect 예제</h2>

    <div>
      <p>Count: {{ count }}</p>
      <button @click="increment">Increment</button>
    </div>

    <div>
      <p>Watch Count: {{ message }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, watchEffect } from 'vue'

const count = ref(0)
const message = ref('')

const increment = () => {
  count.value++
}

// watchEffect: 자동으로 의존성 추적
watchEffect(() => {
  message.value = `Count is: ${count.value}`
})
</script>

<style scoped>
div {
  margin: 20px;
}

button {
  margin: 5px;
  padding: 8px 16px;
  cursor: pointer;
}

.note {
  color: #666;
  font-style: italic;
  margin-top: 20px;
}
</style>