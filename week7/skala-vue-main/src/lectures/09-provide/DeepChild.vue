<template>
  <div class="container">
    <h2>깊은 자식 컴포넌트</h2>
    <div><b>메시지(inject):</b> {{ injectedMessage }}</div>
  </div>
</template>

<script setup>
import { inject } from 'vue';

const injectedMessage = inject('message');
</script>

<style scoped>
h2 {
  color: #42b983;
}

.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  font-family: Arial, sans-serif;
  border: 2px solid #42b983;
}
</style>