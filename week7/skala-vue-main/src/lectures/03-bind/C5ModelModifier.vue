<template>

  <div>
    <input v-model.trim="message" placeholder="Type something">
    <p>Trimmed Message: "{{ message }}"</p>
  </div>

  <div>
    <input v-model.number="age" placeholder="Enter your age">
    <p>Your age plus 5 is: {{ agePlusFive }}</p>
  </div>
</template>

<script setup>

import { ref, computed } from 'vue';

const message = ref("");
const age = ref(null);

const agePlusFive = computed(() => {
  return age.value + 5;
});
</script>