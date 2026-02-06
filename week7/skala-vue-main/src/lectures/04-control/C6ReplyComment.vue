<template>
  <div class="reply-comment">
    <h2>댓글 달기</h2>

    <!-- 댓글 입력 영역 -->
    <div class="comment-input">
      <input v-model="newComment" type="text" placeholder="댓글을 입력하세요" @keyup.enter="addComment" />
      <button @click="addComment">등록</button>
    </div>

    <!-- 댓글 목록 -->
    <ul class="comment-list">
      <li v-for="comment in comments" :key="comment.id" class="comment-item">
        {{ comment.id }}. {{ comment.text }}
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const newComment = ref('');
const comments = ref([]);
const nextId = ref(1);

const addComment = () => {
  // 빈 문자열 체크
  if (newComment.value.trim() === '') {
    return;
  }

  // 새 댓글 추가
  comments.value.push({
    id: nextId.value++,
    text: newComment.value
  });

  // 입력창 초기화
  newComment.value = '';
};
</script>

<style scoped>
.reply-comment {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
}

.comment-input {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.comment-input input {
  flex: 1;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.comment-input button {
  padding: 10px 20px;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.comment-input button:hover {
  background-color: #35a372;
}

.comment-list {
  list-style: none;
  padding: 0;
}

.comment-item {
  padding: 15px;
  margin-bottom: 10px;
  background-color: #f5f5f5;
  border-radius: 4px;
  border-left: 3px solid #42b983;
}
</style>