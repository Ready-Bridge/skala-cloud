<template>
  <div>
    <h1>Composition API Counter</h1>
    <p>Count: {{ count }}</p>
    <button @click="increment">Increment</button>
  </div>
</template>

<script setup>
import { ref } from 'vue';
const count = ref(0); // 상태 정의
const increment = () => {
  count.value++; // 메서드 정의
};
</script>

<style>
button {
  padding: 8px 16px;
  font-size: 16px;
  background-color: blue;
}
</style>
