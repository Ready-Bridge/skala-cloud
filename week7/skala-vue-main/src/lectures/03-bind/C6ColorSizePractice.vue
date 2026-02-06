<template>
  <div class="container">
    <h2>색상과 사이즈 변경</h2>

    <div class="input-section">
      <div class="input-group">
        <label>색상 (영문):</label>
        <input v-model="color" type="text" placeholder="예: red, blue, green" />
      </div>

      <div class="input-group">
        <label>사이즈 (px):</label>
        <input v-model="size" type="number" placeholder="예: 200" />
      </div>

      <button @click="applyStyle">적용</button>
    </div>

    <div class="box" :style="boxStyle">스타일 적용 박스</div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'

const color = ref('lightgray')
const size = ref('150')

const boxStyle = reactive({
  backgroundColor: 'lightgray',
  width: '150px',
  height: '150px'
})

const applyStyle = () => {
  if (color.value) {
    boxStyle.backgroundColor = color.value
  }
  if (size.value) {
    boxStyle.width = `${size.value}px`
    boxStyle.height = `${size.value}px`
  }
}
</script>

<style scoped>
.container {
  padding: 20px;
  max-width: 600px;
  margin: 0 auto;
}

h2 {
  margin-bottom: 20px;
}

.input-section {
  margin-bottom: 30px;
  padding: 20px;
  background-color: #f5f5f5;
  border-radius: 8px;
}

.input-group {
  margin-bottom: 15px;
}

.input-group label {
  display: inline-block;
  width: 120px;
  font-weight: bold;
}

.input-group input {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  width: 200px;
}

button {
  margin-top: 10px;
  padding: 10px 30px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
}

button:hover {
  background-color: #45a049;
}

.box {
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 20px auto;
  border: 2px solid #333;
  border-radius: 8px;
  transition: all 0.3s ease;
}
</style>