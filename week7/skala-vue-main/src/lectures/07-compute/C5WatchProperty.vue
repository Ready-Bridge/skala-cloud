<template>
  <div class="watch-container">
    <h2>4. 객체의 특정 속성 감시 (getter 함수)</h2>

    <section class="watch-section">
      <div class="control-group">
        <label>제품명: </label>
        <input v-model="product.name" type="text" />
        <label>가격: </label>
        <input v-model.number="product.price" type="number" />
        <label>재고: </label>
        <input v-model.number="product.stock" type="number" />
        <p class="info">제품 정보: {{ product }}</p>
        <p class="info">가격 변경 로그: {{ priceLog }}</p>
        <p class="notice">💡 제품명이나 재고를 변경해도 Watch가 실행되지 않습니다!</p>
      </div>

      <div class="explanation">
        <h3>💡 설명</h3>
        <ul>
          <li>getter 함수 <code>() => product.price</code>를 사용해 특정 속성만 감시합니다.</li>
          <li>객체 전체를 감시하지 않아 성능이 향상됩니다.</li>
          <li>다른 속성의 변경은 감지하지 않습니다.</li>
          <li>필요한 속성만 선택적으로 감시할 때 유용합니다.</li>
        </ul>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'

// 객체의 특정 속성 감시
const product = reactive({
  name: '노트북',
  price: 1500000,
  stock: 10
})
const priceLog = ref('대기 중...')

// getter 함수로 특정 속성만 감시
watch(
  () => product.price,
  (newVal, oldVal) => {
    priceLog.value = `가격 변경: ${oldVal.toLocaleString()}원 → ${newVal.toLocaleString()}원`
    console.log('가격 변경:', { oldVal, newVal })
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
