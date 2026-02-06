<template>
  <div class="watch-container">
    <h2>6. 다중 소스 감시 (배열로 여러 값 감시)</h2>

    <section class="watch-section">
      <div class="control-group">
        <label>첫 번째 값: </label>
        <input v-model="value1" type="text" />
        <label>두 번째 값: </label>
        <input v-model="value2" type="text" />
        <p class="info">합계: {{ value1 + ' + ' + value2 }}</p>
        <p class="info">다중 감시 로그: {{ multiLog }}</p>
      </div>

      <div class="explanation">
        <h3>💡 설명</h3>
        <ul>
          <li>배열 <code>[value1, value2]</code>로 여러 값을 동시에 감시합니다.</li>
          <li>어느 하나라도 변경되면 콜백 함수가 실행됩니다.</li>
          <li>콜백에서 각각의 새 값과 이전 값을 배열로 받습니다.</li>
          <li>서로 관련된 여러 값을 동시에 추적할 때 유용합니다.</li>
        </ul>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

// 다중 소스 감시
const value1 = ref('Hello')
const value2 = ref('World')
const multiLog = ref('대기 중...')

watch(
  [value1, value2],
  ([newVal1, newVal2], [oldVal1, oldVal2]) => {
    multiLog.value = `값1: ${oldVal1}→${newVal1}, 값2: ${oldVal2}→${newVal2}`
    console.log('다중 값 변경:', {
      value1: { old: oldVal1, new: newVal1 },
      value2: { old: oldVal2, new: newVal2 }
    })
  }
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
