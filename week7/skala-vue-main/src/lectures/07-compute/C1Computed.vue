<template>
  <h2>Computed 기본 연산</h2>
  <p>이름(firstName): <input v-model="firstName" /></p>
  <p>성(lastName): <input v-model="lastName" /></p>
  <p>풀네임(computed): {{ fullName }}</p>

  <h2>Computed 배열 필터링</h2>
  <p>
    카테고리:
    <select v-model="keyword">
      <option value="">전체</option>
      <option value="과일">과일</option>
      <option value="채소">채소</option>
    </select>
  </p>
  <ul>
    <li v-for="(item, index) in filteredItems" :key="index">
      {{ item.name }} ({{ item.category }})
    </li>
  </ul>

</template>

<script setup>
import { ref, computed } from 'vue'

const firstName = ref('Gildong')
const lastName = ref('Hong')
const fullName = computed(() => `${firstName.value} ${lastName.value}`)

const items = ref([
  { name: '사과', category: '과일' },
  { name: '바나나', category: '과일' },
  { name: '당근', category: '채소' },
  { name: '오이', category: '채소' },
  { name: '파인애플', category: '과일' }
])

const keyword = ref('')

const filteredItems = computed(() =>
  items.value.filter(item => keyword.value === '' || item.category === keyword.value
  ))

</script>
