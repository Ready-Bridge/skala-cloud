<template>
  <div>
    <input v-model="inputValue" placeholder="내용을 입력하세요" />
    <button @click="showMessage">확인</button>

    <div> Message(보간법): {{ message }} </div>
    <div v-text="textMessage"> </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const inputValue = ref('')
const message = ref('')
const textMessage = ref('Message(디렉티브): ')

function showMessage() {
  message.value = inputValue.value;
  textMessage.value = 'Message(디렉티브): ' + inputValue.value;
}
</script>
