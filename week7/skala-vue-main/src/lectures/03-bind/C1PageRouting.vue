<template>
  <div>
    <label for="loginStatus">로그인 상태:</label>
    <input id="loginStatus" type="checkbox" v-model="isLoggedIn" />
    <br /><br />
    <a id="myLink" :href="pageUrl">내 페이지</a>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

const isLoggedIn = ref(false);

const pageUrl = computed(() => {
  return isLoggedIn.value ? 'https://google.com' : 'https://naver.com';
});
</script>
