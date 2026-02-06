<template>
  <!-- class 바인딩 -->
  <div :class="{ bigText: isBig }">
    클래스 방식: 글자 크기가 커지거나 작아집니다.
  </div>
  <!-- style 바인딩 -->
  <div :style="{ fontSize: isBig ? '24px' : '14px' }">
    스타일 방식: 글자 크기가 커지거나 작아집니다.
  </div>
</template>

<script setup>
import { ref } from 'vue'
const isBig = ref(true)
</script>

<style>
.bigText {
  font-size: 24px;
}
</style>
