<template>
  <div class="watch-container">
    <h2>1. 기본 Watch (단일 값 감시)</h2>

    <section class="watch-section">
      <div class="control-group">
        <label>메시지: </label>
        <input v-model="message" type="text" placeholder="메시지를 입력하세요" />
        <p>현재 값: {{ message }}</p>
        <p class="info">Watch 로그: {{ messageLog }}</p>
      </div>

      <div class="explanation">
        <h3>💡 설명</h3>
        <ul>
          <li><code>watch()</code> 함수는 반응형 데이터의 변경을 감시합니다.</li>
          <li>첫 번째 인자: 감시할 ref 또는 reactive 값</li>
          <li>두 번째 인자: 콜백 함수 (newVal, oldVal)</li>
          <li>값이 변경될 때마다 자동으로 실행됩니다.</li>
        </ul>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

// 기본 Watch
const message = ref('')
const messageLog = ref('대기 중...')

watch(message, (newVal, oldVal) => {
  messageLog.value = `"${oldVal}" → "${newVal}" 로 변경됨`
  console.log('메시지 변경:', { oldVal, newVal })
})
</script>

<style scoped>
.watch-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  font-family: Arial, sans-serif;
}

h2 {
  color: #42b983;
  text-align: center;
  margin-bottom: 30px;
}

.watch-section {
  background: #f9f9f9;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 20px;
}

label {
  font-weight: bold;
  color: #2c3e50;
  margin-top: 5px;
}

input {
  padding: 8px 12px;
  border: 2px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.3s;
}

input:focus {
  outline: none;
  border-color: #42b983;
}

.info {
  padding: 10px;
  background: #e8f5e9;
  border-left: 4px solid #42b983;
  border-radius: 4px;
  margin: 5px 0;
  font-size: 14px;
  color: #2c3e50;
  word-break: break-all;
}

p {
  margin: 5px 0;
}

.explanation {
  background: #fff3cd;
  border: 2px solid #ffc107;
  border-radius: 8px;
  padding: 15px;
  margin-top: 20px;
}

.explanation h3 {
  color: #856404;
  margin-top: 0;
  margin-bottom: 10px;
}

.explanation ul {
  margin: 0;
  padding-left: 20px;
}

.explanation li {
  margin-bottom: 8px;
  color: #856404;
}

.explanation code {
  background: #fff;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
  color: #e83e8c;
}
</style>
