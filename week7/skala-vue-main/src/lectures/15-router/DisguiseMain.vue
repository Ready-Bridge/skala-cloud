<template>
  <div>
    <h1>🧙 둔갑술 선택 메뉴</h1>
    <button @click="goToDisguise('호랑이')">호랑이로 둔갑</button>
    <button @click="goToDisguise('도깨비')">도깨비로 둔갑</button>
    <p style="color: red; font-weight: bold;">
      Vue Router를 설정한 후 /pages 폴더에서 작업 하세요.
    </p>
  </div>
</template>
<script setup>
// import { useRouter } from 'vue-router'

// const router = useRouter()

// function goToDisguise(target) {
//   // “/disguise?target=호랑이” 형태로 경로 전환
// }
</script>

<style scoped>
button {
  margin: 8px;
  padding: 12px 24px;
  font-size: 16px;
  cursor: pointer;
}
</style>