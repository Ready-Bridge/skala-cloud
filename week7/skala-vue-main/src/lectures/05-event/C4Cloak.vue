<template>
  <div>
    <h2>v-cloak 디렉티브 예제</h2>
    <div v-cloak class="message">
      {{ message }}
    </div>
    <div v-cloak class="data">
      <p>사용자 이름: {{ user.name }}</p>
      <p>이메일: {{ user.email }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const message = ref('이 메시지는 Vue가 로드된 후에만 표시됩니다.');
const user = ref({
  name: '홍길동',
  email: 'hong@example.com'
});
</script>

<style scoped>
/* v-cloak 디렉티브가 있는 요소를 숨김 */
[v-cloak] {
  display: none;
}

.message {
  padding: 20px;
  background-color: #f0f0f0;
  margin: 10px 0;
  border-radius: 5px;
}

.data {
  padding: 15px;
  background-color: #e3f2fd;
  border-radius: 5px;
}
</style>