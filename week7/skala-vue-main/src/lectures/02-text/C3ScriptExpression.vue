<template>
  <div>
    <p>{{ 1 + 2 }}</p>
    <p>{{ message + '님 환영합니다!' }}</p>
    <p>{{ price * quantity }}원</p>
    <p>{{ isLogin ? '로그인' : '로그아웃' }}</p>
  </div>
</template>

<script setup>
const message = '홍길동'
const price = 5000
const quantity = 3
const isLogin = true
</script>
