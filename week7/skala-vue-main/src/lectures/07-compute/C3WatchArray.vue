<template>
  <div class="watch-container">
    <h2>2. 배열 감시 (deep: true)</h2>

    <section class="watch-section">
      <div class="control-group">
        <input v-model="newItem" type="text" placeholder="항목 입력" />
        <div class="button-group">
          <button @click="addItem">항목 추가</button>
          <button @click="removeLastItem">마지막 항목 제거</button>
        </div>
        <ul>
          <li v-for="(item, index) in items" :key="index">{{ item }}</li>
        </ul>
        <p class="info">배열 길이: {{ items.length }}</p>
        <p class="info">Watch 로그: {{ arrayLog }}</p>
      </div>

      <div class="explanation">
        <h3>💡 설명</h3>
        <ul>
          <li>배열의 변경을 감시하려면 <code>deep: true</code> 옵션이 필요합니다.</li>
          <li>배열의 요소 추가, 제거, 수정 등 모든 변경을 감지합니다.</li>
          <li><code>ref([])</code>로 선언된 배열도 깊은 감시가 가능합니다.</li>
          <li>성능을 위해 필요한 경우에만 deep 옵션을 사용하세요.</li>
        </ul>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

// 배열 감시
const items = ref(['사과', '바나나', '오렌지'])
const newItem = ref('')
const arrayLog = ref('대기 중...')

const addItem = () => {
  if (newItem.value.trim()) {
    items.value.push(newItem.value)
    newItem.value = ''
  }
}

const removeLastItem = () => {
  if (items.value.length > 0) {
    items.value.pop()
  }
}

watch(
  items,
  (newVal, oldVal) => {
    arrayLog.value = `배열 변경 감지! 항목 수: ${oldVal.length} → ${newVal.length}`
    console.log('배열 변경:', { oldVal: [...oldVal], newVal: [...newVal] })
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

.button-group {
  display: flex;
  gap: 10px;
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

ul {
  list-style-type: none;
  padding: 0;
  margin: 10px 0;
}

li {
  padding: 8px 12px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  margin-bottom: 5px;
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
