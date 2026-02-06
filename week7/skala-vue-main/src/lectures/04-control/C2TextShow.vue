<template>
  <div>
    <button @click="toggleVisibility">Toggle Visibility</button>
    <p v-show="isVisible">This text is visible!</p>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const isVisible = ref(true);

const toggleVisibility = () => {
  isVisible.value = !isVisible.value;
};
</script>
