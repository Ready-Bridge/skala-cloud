<template>
  <div class="bmi-container">
    <h2>홍길동의 BMI 계산기</h2>

    <section class="bmi-section">
      <div class="control-group">
        <p>
          <label>키 (cm): </label>
          <input v-model.number="heightCm" type="number" placeholder="키를 입력하세요" />
        </p>
        <p>
          <label>체중 (kg): </label>
          <input v-model.number="weightKg" type="number" placeholder="체중을 입력하세요" />
        </p>
        <p class="info">BMI 지수: {{ bmi.toFixed(2) }}</p>
        <p class="info">판정: {{ judgment }}</p>
      </div>

      <div class="explanation">
        <h3>💡 설명</h3>
        <ul>
          <li>키와 체중을 입력받아 BMI 지수를 계산합니다.</li>
          <li>계산된 BMI 값이 25 이상이면 판정 메시지에 "다이어트 하세요"를 추가합니다.</li>
          <li><code>computed()</code>로 BMI를 계산하고, <code>watch()</code>로 판정을 감시합니다.</li>
        </ul>
      </div>
    </section>
  </div>
</template>

<script setup>
// 실습을 위해 변수만 선언
import { ref, } from 'vue'

const heightCm = ref(0)
const weightKg = ref(0)
const judgment = ref('')
const bmi = ref(0)

</script>

<style scoped>
.bmi-container {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 8px;
  background-color: #f9f9f9;
}

.control-group {
  margin-bottom: 12px;
}

.info {
  margin-top: 8px;
  font-weight: bold;
}

.explanation {
  margin-top: 20px;
  padding: 12px;
  border: 1px dashed #aaa;
  border-radius: 4px;
  background-color: #fff;
}
</style>