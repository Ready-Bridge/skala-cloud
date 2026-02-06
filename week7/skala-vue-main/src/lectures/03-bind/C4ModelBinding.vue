<template>
  <div>
    <input v-model="message" placeholder="Type something">
    <p>Message: {{ message }}</p>
  </div>

  <!--텍스트 입력 바인딩-->
  <div>
    <input v-model="message" placeholder="Type something">
    <p>Message: {{ message }}</p>
  </div>

  <!--체크박스 바인딩-->
  <div>
    <input type="checkbox" v-model="message">
    <p>Checked: {{ message }}</p>
  </div>

  <!--라디오 버튼 바인딩-->
  <div>
    <input type="radio" value="Option 1" v-model="message"> Option 1
    <input type="radio" value="Option 2" v-model="message"> Option 2
    <p>Selected: {{ message }}</p>
  </div>

  <!--셀렉트 박스 바인딩-->
  <div>
    <select v-model="message">
      <option value="A">Option A</option>
      <option value="B">Option B</option>
      <option value="C">Option C</option>
    </select>
    <p>Selected: {{ message }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue';
const message = ref("");
</script>

<style>
div {
  margin-bottom: 12px;
}
</style>
