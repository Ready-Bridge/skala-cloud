<template>
  <div>
    <h1>Options API Counter</h1>
    <p>Count: {{ count }}</p>
    <button @click="increment">Increment</button>
  </div>
</template>

<script>
export default {
  data() {
    return {
      count: 0, // 상태 정의
    };
  },
  methods: {
    increment() {
      this.count++; // 메서드 정의
    },
  },
};
</script>

<style>
button {
  padding: 8px 16px;
  font-size: 16px;
  background-color: blue;
}
</style>
