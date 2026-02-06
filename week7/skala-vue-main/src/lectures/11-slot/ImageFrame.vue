<template>
  <div class="image-frame">
    <div class="frame-border">
      <div class="image-container">
        <slot></slot>
      </div>
      <div class="frame-info">
        <h3 class="frame-title">작품명: {{ title }}</h3>
        <p class="frame-artist">작가: {{ artist }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: String,
  artist: String,
})
</script>

<style scoped>
.image-frame {
  display: inline-block;
  padding: 20px;
  background-color: #f5f5f5;
}

.frame-border {
  border: 8px solid #333;
  background-color: white;
  padding: 15px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.image-container {
  margin-bottom: 15px;
  background-color: #fafafa;
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.frame-info {
  padding: 10px;
  border-top: 1px solid #ddd;
  text-align: left;
}

.frame-title {
  margin: 0 0 5px 0;
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.frame-artist {
  margin: 0 0 5px 0;
  font-size: 14px;
  color: #666;
  font-style: italic;
}

.frame-size {
  margin: 0;
  font-size: 12px;
  color: #999;
}
</style>