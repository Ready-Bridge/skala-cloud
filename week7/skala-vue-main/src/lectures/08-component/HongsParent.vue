<template>
  <div class="parent">
    <h2>홍판서네 자식들</h2>

    <section class="children">
      <HongsChild name="홍길동" :assets="assets.forSon" @money="takeMoney" />
      <HongsChild name="홍길순" :assets="assets.forDaughter" @money="takeMoney" />
    </section>

    <section class="result">
      <h3>자녀가 보내준 용돈 합계 : {{ totalAllowance.toLocaleString() }}원</h3>
      <h4>받은 내역</h4>
      <ul>
        <li v-for="(item, idx) in logs" :key="idx">
          {{ item.from }} → {{ item.amount.toLocaleString() }}원
        </li>
      </ul>
    </section>
  </div>
</template>

<script setup>
import { computed, ref } from "vue";
import HongsChild from "./HongsChild.vue";

const assets = {
  forSon: ["칼", "창"],
  forDaughter: ["기와집", "전답"],
};

const logs = ref([]); // { from: string, amount: number }[]

function takeMoney(from, amount) {
  logs.value.push({ from, amount }); // { from: from, amount: amount }와 동일
}

const totalAllowance = computed(() =>
  logs.value.reduce((sum, x) => sum + x.amount, 0)
);
</script>

<style scoped>
.parent {
  padding: 16px;
  border: 2px solid #ddd;
  border-radius: 8px;
  max-width: 720px;
}

.assets,
.children,
.result {
  margin-top: 16px;
  padding: 12px;
  border: 1px solid #eee;
  border-radius: 8px;
}

.children>*+* {
  margin-top: 12px;
}
</style>
