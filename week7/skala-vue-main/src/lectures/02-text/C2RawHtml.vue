<template>
  <div>
    <input v-model="inputValue" placeholder="내용을 입력하세요" />
    <button @click="showMessage">확인</button>
    <div v-html="message"></div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const inputValue = ref('')
const message = ref('')

function showMessage() {
  message.value = inputValue.value;

  // XSS 취약점 예시
  // <img src="x"  onerror="window.location.href='https://google.com'" />
}
</script>
