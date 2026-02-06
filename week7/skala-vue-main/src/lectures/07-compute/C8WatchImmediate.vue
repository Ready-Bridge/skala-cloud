<template>
  <div class="watch-container">
    <h2>7. Immediate 옵션 (즉시 실행)</h2>

    <section class="watch-section">
      <div class="control-group">
        <label>카운터: </label>
        <input v-model.number="counter" type="number" />
        <div class="button-group">
          <button @click="counter++">증가</button>
          <button @click="counter--">감소</button>
          <button @click="counter = 0">리셋</button>
        </div>
        <p class="info">현재 카운터: {{ counter }}</p>
        <p class="info">Immediate 로그: {{ immediateLog }}</p>
        <p class="notice">💡 페이지를 새로고침하면 즉시 로그가 생성됩니다!</p>
      </div>

      <div class="explanation">
        <h3>💡 설명</h3>
        <ul>
          <li><code>immediate: true</code> 옵션은 컴포넌트 마운트 시 즉시 watch를 실행합니다.</li>
          <li>초기값으로도 콜백 함수가 호출됩니다.</li>
          <li>첫 실행 시 oldVal은 undefined입니다.</li>
          <li>초기 데이터 로딩이나 초기 상태 설정에 유용합니다.</li>
        </ul>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

// Immediate 옵션
const counter = ref(0)
const immediateLog = ref('')

watch(
  counter,
  (newVal, oldVal) => {
    immediateLog.value = `카운터 변경: ${oldVal ?? '초기값'} → ${newVal} (${new Date().toLocaleTimeString()})`
    console.log('카운터 변경 (immediate):', { oldVal, newVal })
  },
  { immediate: true } // 컴포넌트 마운트 시 즉시 실행
)
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

.button-group {
  display: flex;
  gap: 10px;
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

button {
  padding: 10px 20px;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
  flex: 1;
}

button:hover {
  background-color: #35a372;
}

button:active {
  transform: translateY(1px);
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

.notice {
  padding: 10px;
  background: #fff3e0;
  border-left: 4px solid #ff9800;
  border-radius: 4px;
  margin: 10px 0;
  font-size: 14px;
  color: #e65100;
  font-weight: bold;
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
