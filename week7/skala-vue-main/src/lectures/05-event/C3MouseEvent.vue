<template>
  <div @mousemove="handleMouseMove">
    마우스를 올려보세요
  </div>
  <p>마우스 좌표: x = {{ mouseX }}, y = {{ mouseY }}</p>
</template>

<script setup>
import { ref } from 'vue'

const mouseX = ref(0)
const mouseY = ref(0)

const handleMouseMove = (event) => {
  mouseX.value = event.clientX
  mouseY.value = event.clientY
}

// 마우스가 div 영역을 벗어났을 때 좌표를 초기화하는 기능 추가
</script>

<style scoped>
div {
  cursor: pointer;
  width: 300px;
  height: 150px;
  border: 2px dashed #333;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 8px;
  font-size: 16px;
  background-color: #f9f9f9;
}
</style>