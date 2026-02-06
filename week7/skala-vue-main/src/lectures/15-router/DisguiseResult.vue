<template>
  <div>
    <h1>둔갑술 시전!</h1>
    <p>홍길동이 <strong>{{ target }}</strong>(으)로 변신했습니다!</p>

    <p style="color: red; font-weight: bold;">
      ※ Vue Router를 설정한 후 /pages 폴더에서 작업 하세요.
    </p>
  </div>
</template>


<script setup>
import { onMounted, ref } from 'vue'
// import { useRoute, useRouter } from 'vue-router'

const target = ref('???')

// const route = useRoute()
// const router = useRouter()

// onMounted(() => {
//   if (route.query.target) {
//     target.value = route.query.target
//     // 브라우저 URL에서 query 부분 제거
//   }
// })

</script>
