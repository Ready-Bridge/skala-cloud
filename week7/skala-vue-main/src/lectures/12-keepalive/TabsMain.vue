<template>
  <div class="tabs-container">
    <h3>KeepAlive 유무 비교</h3>
    <div class="tabs-header">
      <button @click="selectTab(TabChildOne)" :class="['tab-button', { active: currentTab === TabChildOne }]">
        Tab 1
      </button>
      <button @click="selectTab(TabChildTwo)" :class="['tab-button', { active: currentTab === TabChildTwo }]">
        Tab 2
      </button>
    </div>

    <div class="tabs-content">
      <!-- <keep-alive>
        <component :is="currentTab" />
      </keep-alive> -->
      <component :is="currentTab" />
    </div>
  </div>
</template>

<script setup>
import { ref, markRaw } from 'vue'

import TabChildOne from './TabChildOne.vue'
import TabChildTwo from './TabChildTwo.vue'

const currentTab = ref(markRaw(TabChildOne))

const selectTab = (tab) => {
  currentTab.value = markRaw(tab)
}
</script>

<style scoped>
.tabs-container {
  max-width: 800px;
  margin: 20px auto;
}

.tabs-header {
  display: flex;
  border-bottom: 2px solid #e0e0e0;
}

.tab-button {
  padding: 12px 24px;
  border: none;
  background: none;
  cursor: pointer;
  font-size: 16px;
  color: #666;
  border-bottom: 3px solid transparent;
  transition: all 0.3s;
}

.tab-button:hover {
  color: #333;
  background: #f5f5f5;
}

.tab-button.active {
  color: #42b983;
  border-bottom-color: #42b983;
  font-weight: 600;
}

.tabs-content {
  padding: 20px;
  background: #fff;
}
</style>
