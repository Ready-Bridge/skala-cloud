<template>
  <h2>reactive 기초 예제</h2>
  <div>
    <p>이름: <input v-model="user.name" /></p>
    <p>{{ user.name }}: {{ user.age }} <button @click="user.age++">한 살 더</button></p>
    <hr>
    <p>과일 목록: {{ fruits.join(', ') }}</p>
    <button @click="fruits.push('귤')">과일 추가</button>
  </div>
</template>

<script setup>
import { reactive } from 'vue'

const user = reactive({ name: '홍길동', age: 20 })
const fruits = reactive(['사과', '배'])
</script>
