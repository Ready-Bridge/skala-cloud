<template>
  <div>
    <h2>입력창 자동 포커스 예제</h2>
    <p>버튼 클릭 시 입력창에 자동으로 포커스가 이동해야 합니다.</p>
    <p>개발자 도구를 통해 console 창을 확인하세요.</p>
    <button @click="showInputBox">입력창 열기</button>
    <div v-if="isVisible">
      <input ref="inputRef" placeholder="이름 입력" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const isVisible = ref(false)
const inputRef = ref(null)

function showInputBox() {
  isVisible.value = true
  inputRef.value.focus()
}
</script>
