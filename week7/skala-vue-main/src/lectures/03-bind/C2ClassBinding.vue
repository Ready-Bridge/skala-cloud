<template>
  <div>
    <!-- 1. 문자열 바인딩 -->
    <button :class="buttonType">문자열 바인딩</button>

    <!-- 2. 객체 바인딩 -->
    <button :class="{ base: true, primary: true, rounded: isRounded }">객체 바인딩</button>

    <!-- 3. 배열 바인딩 -->
    <button :class="['base', 'primary', 'rounded']">배열 바인딩</button>

    <!-- 4. 조합 바인딩 (배열 + 객체) -->
    <button :class="['base', buttonType, { rounded: isRounded, highlight: isHighlighted }]">
      조합 바인딩
    </button>

    <!-- 5. 다중 객체 조합 -->
    <button :class="[{ base: true, secondary: buttonType === 'secondary' }, { rounded: isRounded }]">
      다중 객체 조합
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue';
const buttonType = ref('primary'); // 'primary' or 'secondary'
const isRounded = ref(true);
const isHighlighted = ref(false);
</script>

<style>
.base {
  padding: 10px 16px;
  font-size: 16px;
  margin: 8px;
  transition: 0.3s;
}

.primary {
  background-color: #42b983;
  color: white;
}

.secondary {
  background-color: #ddd;
  color: black;
}

.rounded {
  border-radius: 10px;
}

.highlight {
  box-shadow: 0 0 6px rgba(255, 215, 0, 0.6);
}
</style>
