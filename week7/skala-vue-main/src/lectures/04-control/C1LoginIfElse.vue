<template>
  <div>
    <button @click="toggleLogin">Toggle Login</button>
    <p v-if="isLoggedIn">Welcome back!</p>
    <p v-else>Please log in.</p>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const isLoggedIn = ref(false);

const toggleLogin = () => {
  isLoggedIn.value = !isLoggedIn.value;
};
</script>
