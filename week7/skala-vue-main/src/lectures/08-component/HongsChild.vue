<template>
  <div class="child">
    <p><b>자식 이름:</b> {{ props.name ? props.name : '나는 누구인가?' }}</p>
    <div class="inherit">
      <p><b>부모에게 받은 자산(props)</b></p>
      <ol>
        <li v-for="(value, index) in props.assets" :key="index">
          {{ value }}
        </li>
      </ol>
    </div>
    <div class="allowance">
      <label style="font-weight: bold;">
        부모님께 드릴 용돈(원):
        <input type="number" min="0" step="10000" v-model.number="amount" placeholder="예: 50000" />
      </label>
      <button @click="sendMoney" :disabled="props.assets === undefined || props.assets.length === 0">
        용돈 보내기(emit)
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";

const props = defineProps({
  name: String,
  assets: Array,
});

const emit = defineEmits(["money"]);

const amount = ref(0);

function sendMoney() {
  emit("money", props.name, amount.value);
  amount.value = 0;
}
</script>

<style scoped>
.child {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background-color: #f9f9f9;
}

.allowance {
  margin-top: 4px;
  display: flex;
  gap: 4px;
  align-items: center;
  flex-wrap: wrap;
}

input {
  margin-left: 4px;
  padding: 4px;
  width: 180px;
}

button {
  padding: 4px;
  cursor: pointer;
}
</style>
