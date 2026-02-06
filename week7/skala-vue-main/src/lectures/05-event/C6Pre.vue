<template>
  <div>
    <div v-pre style="margin-bottom: 8px;">
      보간법 기호가 그대로 출력됩니다. {{ message }}
    </div>
    <button @click="updateMessage">메시지 업데이트</button>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const message = ref("이 메시지는 첫 번째 렌더링 후에는 변경되지 않습니다.");

const updateMessage = () => {
  message.value = "업데이트된 메시지.";
};
</script>
