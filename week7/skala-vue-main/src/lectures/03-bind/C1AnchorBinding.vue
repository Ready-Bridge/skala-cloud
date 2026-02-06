<template>
  <div>
    <a v-bind:href="url">Visit Vue.js(v-bind:href)</a><br />
    <a :href="url">Visit Vue.js(:href)</a>
  </div>
</template>

<script setup>
const url = "https://vuejs.org";
</script>
