<template>
  <NamedSlot>
    <template #header>
      <h3>여기에 Header 콘텐츠를 넣었습니다</h3>
    </template>

    <img src="./kdh-1.png" />

    <template #footer>
      <p>여기가 Footer 콘텐츠입니다</p>
    </template>
  </NamedSlot>
</template>


<script setup>
import NamedSlot from './NamedSlot.vue';
</script>
