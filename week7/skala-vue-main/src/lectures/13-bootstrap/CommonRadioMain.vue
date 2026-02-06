<template>
  <div>
    CommonRadio를 이용해 성별, 학교를 선택할 수 있는 화면 만들기
  </div>
</template>

<script setup>
import { ref } from "vue"

const genderOptions = ref([
  { label: "남", value: "m" },
  { label: "여", value: "f" },
])

const schoolOptions = ref([
  { label: "초등학교", value: "01" },
  { label: "중학교", value: "02" },
  { label: "고등학교", value: "03" },
  { label: "대학교", value: "04" },
])

</script>