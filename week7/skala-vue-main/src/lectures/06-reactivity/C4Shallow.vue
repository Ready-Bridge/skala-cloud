<template>
  <div>
    <h2>shallowRef 기초 예제</h2>
    <h4>{{ user.name }} - {{ user.address.city }}</h4>
    <div>
      <label for="name">이름:</label>
      <input id="name" v-model="userName" />
      <button @click="changeName">이름 변경</button>
    </div>
    <div>
      <label for="city">도시:</label>
      <input id="city" v-model="userCity" />
      <button @click="changeCity">도시 변경</button>
    </div>
  </div>
</template>

<script setup>
import { ref, } from 'vue'
import { userRef, updateName, updateCity } from '@/lectures/06-reactivity/shallow-ref.js'

const user = userRef
const userName = ref('')
const userCity = ref('')

function changeName() {
  updateName(userName.value)
}

function changeCity() {
  updateCity(userCity.value) // 화면에는 반영되지 않음
}
</script>

<style scoped>
button {
  margin-right: 1em;
}
</style>
