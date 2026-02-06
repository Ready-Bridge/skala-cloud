<template>
  <div>
    <h2>✅ 반응형 사용자 (state1)</h2>
    <p>이름: {{ state1.user.name }} / 나이: {{ state1.user.age }}</p>
    <p>기술: {{ state1.skills.join(', ') }}</p>
    <button @click="incrementAge(state1)">나이 증가</button>
    <button @click="addSkill(state1)">기술 추가</button>
    <hr />

    <h2>🚫 markRaw 사용자 (state2)</h2>
    <p>이름: {{ state2.user.name }} / 나이: {{ state2.user.age }}</p>
    <p>기술: {{ state2.skills.join(', ') }}</p>
    <button @click="incrementAge(state2)">나이 증가</button>
    <button @click="addSkill(state2)">기술 추가</button>
  </div>
</template>

<script setup>
import { reactive, markRaw } from 'vue'

const obj = {
  name: '홍길동',
  age: 20
}
const state1 = reactive({
  user: { ...obj }, // ✅ 반응형 유지
  skills: []
})
const state2 = reactive({
  user: markRaw({ ...obj }), // 🚫 반응성 제거
  skills: []
})

function incrementAge(state) {
  state.user.age++
}
function addSkill(state) {
  state.skills.push('기술#' + state.skills.length)
}
</script>
