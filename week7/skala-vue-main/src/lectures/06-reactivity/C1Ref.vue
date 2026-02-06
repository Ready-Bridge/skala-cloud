<template>
  <h2>ref 기초 예제</h2>
  <div>
    <p>카운트: {{ count }}</p>
    <button @click="count++">증가</button>
    <hr>
    <p>활성 상태: {{ isActive ? '활성' : '비활성' }}</p>
    <button @click="isActive = !isActive">토글</button>
    <hr>
    <p>과일 목록: {{ items.join(', ') }}</p>
    <button @click="items.push('귤')">과일 추가</button>
    <hr>
    <p>인물: {{ person.name }} - {{ person.age }} 세</p>
    <button @click="person.age++">나이 증가</button>
  </div>
</template>

<script setup>
import { h, ref } from 'vue'

const count = ref(0)
const isActive = ref(true)
const items = ref(['사과', '배'])
const person = ref({ name: '홍길동', age: 20 })
</script>
