<template>
  <div class="kdh-gallery">
    <h2>케데헌 갤러리</h2>
    <div class="gallery-grid">
      <ImageFrame title="더피" artist="소니픽처스">
        <img src="./kdh-1.png" alt="KDH Photo 1">
      </ImageFrame>

      <ImageFrame title="사자보이즈" artist="소니픽처스">
        <img src="./kdh-2.png" alt="KDH Photo 2">
      </ImageFrame>
    </div>
  </div>
</template>

<script setup>
import ImageFrame from './ImageFrame.vue'
</script>

<style scoped>
.kdh-gallery {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

h2 {
  text-align: center;
  margin-bottom: 30px;
  color: #333;
}

.gallery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}
</style>