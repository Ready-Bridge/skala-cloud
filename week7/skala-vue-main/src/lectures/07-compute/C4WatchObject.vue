<template>
  <div class="watch-container">
    <h2>3. 객체 감시 (deep: true)</h2>

    <section class="watch-section">
      <div class="control-group">
        <label>이름: </label>
        <input v-model="user.name" type="text" />
        <label>나이: </label>
        <input v-model.number="user.age" type="number" />
        <label>이메일: </label>
        <input v-model="user.email" type="email" />
        <p class="info">사용자 정보: {{ user }}</p>
        <p class="info">Watch 로그: {{ userLog }}</p>
      </div>

      <div class="explanation">
        <h3>💡 설명</h3>
        <ul>
          <li><code>reactive()</code>로 생성된 객체는 기본적으로 깊은 반응성을 가집니다.</li>
          <li><code>watch()</code>로 감시할 때 <code>deep: true</code> 옵션을 사용합니다.</li>
          <li>객체의 모든 속성 변경을 감지합니다.</li>
          <li>복잡한 객체 구조에서도 변경 사항을 추적할 수 있습니다.</li>
        </ul>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'

// 객체 감시
const user = reactive({
  name: '홍길동',
  age: 25,
  email: 'hong@example.com'
})
const userLog = ref('대기 중...')

watch(
  user,
  (newVal) => {
    userLog.value = `사용자 정보 변경됨: ${JSON.stringify(newVal)}`
    console.log('사용자 정보 변경:', newVal)
  },
  { deep: true }
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
