<template>
  <div class="watch-container">
    <h2>5. 중첩 객체 감시 (deep watch)</h2>

    <section class="watch-section">
      <div class="control-group">
        <h4>주소 정보</h4>
        <label>도시: </label>
        <input v-model="person.address.city" type="text" />
        <label>거리: </label>
        <input v-model="person.address.street" type="text" />
        <label>우편번호: </label>
        <input v-model="person.address.zipCode" type="text" />

        <h4>연락처</h4>
        <label>휴대폰: </label>
        <input v-model="person.contact.phone" type="text" />
        <label>이메일: </label>
        <input v-model="person.contact.email" type="text" />

        <p class="info">사람 정보: {{ person }}</p>
        <p class="info">중첩 객체 로그: {{ nestedLog }}</p>
      </div>

      <div class="explanation">
        <h3>💡 설명</h3>
        <ul>
          <li>중첩된 객체(객체 안의 객체)의 변경을 감지합니다.</li>
          <li><code>deep: true</code> 옵션으로 모든 깊이의 속성 변경을 추적합니다.</li>
          <li>address.city, contact.phone 등 깊이에 관계없이 모두 감지됩니다.</li>
          <li>복잡한 데이터 구조에서 유용하지만 성능 비용이 있습니다.</li>
        </ul>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'

// 중첩 객체 감시
const person = reactive({
  address: {
    city: '서울',
    street: '강남대로',
    zipCode: '12345'
  },
  contact: {
    phone: '010-1234-5678',
    email: 'person@example.com'
  }
})
const nestedLog = ref('대기 중...')

watch(
  person,
  (newVal) => {
    nestedLog.value = `중첩 객체 변경 감지 - 도시: ${newVal.address.city}, 전화: ${newVal.contact.phone}`
    console.log('중첩 객체 변경:', newVal)
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

h4 {
  color: #42b983;
  margin-top: 15px;
  margin-bottom: 10px;
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
