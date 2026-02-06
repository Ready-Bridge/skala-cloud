<template>
  <h2> reactive의 분해 (toRef)</h2>
  <input v-model="refName" />
  <input v-model="refAge" type="number" />
  <div>{{ refName }}, {{ refAge }}</div>

  <h2> reactive의 분해 (toRefs)</h2>
  <input v-model="name" />
  <input v-model="age" type="number" />
  <div>{{ name }}, {{ age }}</div>

</template>

<script setup>
import { reactive, toRef, toRefs } from 'vue'

const state = reactive({
  name: '홍길동',
  age: 20
})

const refName = toRef(state, 'name')
const refAge = toRef(state, 'age')

const { name, age } = toRefs(state)
</script>
