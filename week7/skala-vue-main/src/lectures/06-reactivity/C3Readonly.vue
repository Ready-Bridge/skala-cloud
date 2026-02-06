<template>
  <h2>readonly 기초 예제</h2>
  <div>
    <p> 오리지날 :
      <span>이름-{{ original.name }}, 나이-{{ original.age }}</span>
      <button @click="updateOriginalAge">한살 더</button>
    </p>
    <p> 리드온리 :
      <span>이름-{{ user.name }}, 나이-{{ user.age }}</span>
      <button @click="updateReadonlyAge">한살 더</button>
    </p>
  </div>
</template>

<script setup>
import { reactive, readonly } from 'vue'

const original = reactive({ name: '홍길동', age: 20 })
const user = readonly(original)

const updateOriginalAge = () => {
  original.age++
}

const updateReadonlyAge = () => {
  try {
    user.age++
  } catch (e) { // vue warning은 catch되지 않음
    alert(`readonly 객체: ${e.message}`)
  }
}
</script>

<style scoped>
p {
  margin-bottom: 1em;
}

button {
  margin-left: 1em;
}
</style>