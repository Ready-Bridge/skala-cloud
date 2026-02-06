<template>
  <div>
    <input v-model="message" placeholder="Enter a message" />
    <p>Message: {{ message }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
const message = ref('')
</script>
