<template>
  <div class="education-container">
    <header class="header">
      <h1>Vue.js 강의 예제 탐색기</h1>
      <div class="controls">
        <div class="select-group">
          <label for="folder-select">📂 폴더: </label>
          <select id="folder-select" v-model="selectedFolder">
            <option value="">-- 폴더 선택 --</option>
            <option v-for="folder in folders" :key="folder" :value="folder">
              {{ folder }}
            </option>
          </select>
        </div>
        <div class="select-group">
          <label for="file-select">📄 파일: </label>
          <select id="file-select" v-model="selectedFile" :disabled="!selectedFolder">
            <option value="">-- 파일 선택 --</option>
            <option v-for="file in availableFiles" :key="file" :value="file">
              {{ file }}
            </option>
          </select>
        </div>
        <div class="file-info-header" v-if="selectedKey">
          <code>📍 {{ displayPath }}</code>
        </div>
      </div>
    </header>

    <main class="content">
      <div v-if="selectedKey" class="split-view">
        <div class="panels" :class="{ 'code-minimized': isCodeMinimized }">
          <div class="code-panel">
            <div class="panel-header">
              <h3>💻 소스 코드</h3>
              <div>
                <button v-if="!isCodeMinimized" class="toggle-button" @click="collapseCodePanel" title="소스코드 축소">
                  <span>⬅</span>
                </button>
                <button v-else class="toggle-button" @click="expandCodePanel" title="소스코드 축소">
                  <span>➡</span>
                </button>
              </div>
            </div>
            <pre class="code-editor"><code class="language-vue" v-html="highlightedCode"></code></pre>
          </div>
          <div class="preview-panel">
            <div class="panel-header">
              <h3>▶️ 실행 결과</h3>
            </div>
            <div class="preview-content">
              <component :is="currentComponent" :key="componentKey" />
            </div>
          </div>
        </div>
      </div>
      <div v-else class="empty-state">
        <p>📁 폴더와 📄 파일을 선택해주세요.</p>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, defineAsyncComponent, watch, shallowRef } from 'vue';
import hljs from 'highlight.js/lib/core';
import javascript from 'highlight.js/lib/languages/javascript';
import xml from 'highlight.js/lib/languages/xml';
import 'highlight.js/styles/github.css';

hljs.registerLanguage('javascript', javascript);
hljs.registerLanguage('xml', xml);

// 패널 크기 조절 상태
const isCodeMinimized = ref(false);

const componentsModules = import.meta.glob('./lectures/**/*.vue');
const rawModules = import.meta.glob('./lectures/**/*.vue', { query: '?raw', import: 'default' });

const allComponents = {};
const allRawSources = {};
const componentsByFolder = {};

for (const path in componentsModules) {
  const componentName = path.replace('./lectures/', '').replace('.vue', '');
  const parts = componentName.split('/');
  const folderName = parts.length > 1 ? parts[0] : '/';
  const fileName = parts.length > 1 ? parts.slice(1).join(' > ') : parts[0];

  if (!componentsByFolder[folderName]) {
    componentsByFolder[folderName] = [];
  }
  componentsByFolder[folderName].push(fileName);

  const fullKey = folderName === '/' ? fileName : `${folderName} > ${fileName}`;
  allComponents[fullKey] = defineAsyncComponent(componentsModules[path]);
  allRawSources[fullKey] = rawModules[path];
}

const folders = computed(() => Object.keys(componentsByFolder).sort());
const selectedFolder = ref('');
const selectedFile = ref('');

const availableFiles = computed(() => {
  if (!selectedFolder.value) return [];
  return (componentsByFolder[selectedFolder.value] || []).sort();
});

const selectedKey = computed(() => {
  if (!selectedFolder.value || !selectedFile.value) return '';
  return selectedFolder.value === '/' ? selectedFile.value : `${selectedFolder.value} > ${selectedFile.value}`;
});

const displayPath = computed(() => {
  if (!selectedKey.value) return '';
  if (selectedFolder.value === '/') return `src/lectures/${selectedFile.value}.vue`;
  return `src/lectures/${selectedKey.value.replace(/ > /g, '/')}.vue`;
});

const sourceCode = ref('');
const editableCode = ref('');
const isCodeModified = ref(false);
const componentKey = ref(0);
const currentComponent = shallowRef(null);

const highlightedCode = computed(() => {
  if (!editableCode.value) return '';
  return hljs.highlight(editableCode.value, { language: 'xml' }).value;
});

const loadSourceCode = async () => {
  if (!selectedKey.value) {
    sourceCode.value = '';
    editableCode.value = '';
    currentComponent.value = null;
    return;
  }

  try {
    const loader = allRawSources[selectedKey.value];
    if (loader) {
      const rawSource = await loader();
      sourceCode.value = rawSource;
      editableCode.value = rawSource;
      isCodeModified.value = false;
      currentComponent.value = allComponents[selectedKey.value];
      componentKey.value++;
    } else {
      sourceCode.value = '// 소스 코드를 찾을 수 없습니다.';
      editableCode.value = sourceCode.value;
      currentComponent.value = null;
    }
  } catch (error) {
    console.error('소스 코드 로드 실패:', error);
    sourceCode.value = '// 소스 코드를 불러오는 중 오류가 발생했습니다.';
    editableCode.value = sourceCode.value;
    currentComponent.value = null;
  }
};

const onCodeChange = () => {
  isCodeModified.value = editableCode.value !== sourceCode.value;
};

const collapseCodePanel = () => {
  // 왼쪽 화살표(◀) 클릭 -> 소스코드 축소 (10:90)
  isCodeMinimized.value = true;
};

const expandCodePanel = () => {
  // 오른쪽 화살표(▶) 클릭 -> 소스코드 확대 (50:50)
  isCodeMinimized.value = false;
};

watch(selectedFolder, () => {
  selectedFile.value = '';
});

watch(selectedKey, loadSourceCode, { immediate: true });
</script>

<style scoped>
.education-container {
  font-family: 'Pretendard', sans-serif;
  width: 100%;
  max-width: 100vw;
  margin: 0;
  padding: 10px 30px 20px;
  min-height: 100vh;
  box-sizing: border-box;
}

.header {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding-bottom: 15px;
  border-bottom: 2px solid #42b883;
  margin-bottom: 15px;
}

h1 {
  color: #2c3e50;
  font-size: 1.4rem;
  margin: 0;
}

.controls {
  display: flex;
  align-items: center;
  gap: 20px;
  background: #f8f9fa;
  padding: 10px 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  flex-wrap: wrap;
}

.file-info-header {
  margin-left: auto;
  color: #666;
}

.file-info-header code {
  background: #eef7f3;
  padding: 6px 12px;
  border-radius: 4px;
  font-family: monospace;
  font-size: 13px;
  color: #35495e;
  border: 1px solid #42b883;
  white-space: nowrap;
}

.select-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.select-group label {
  font-weight: 500;
  white-space: nowrap;
}

select {
  padding: 8px 12px;
  border-radius: 4px;
  border: 1px solid #ddd;
  font-size: 14px;
  min-width: 180px;
  background: white;
  cursor: pointer;
  transition: all 0.2s;
}

select:hover:not(:disabled) {
  border-color: #42b883;
}

select:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
  opacity: 0.6;
}

.panels {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  width: 100%;
  transition: grid-template-columns 0.3s ease;
}

.panels.code-minimized {
  grid-template-columns: 10% 90%;
}

.panels.preview-minimized {
  grid-template-columns: 90% 10%;
}

.code-panel,
.preview-panel {
  background: #fff;
  border: 1px solid #eaeaea;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  height: calc(100vh - 180px);
  min-height: 600px;
}

.panel-header {
  background: linear-gradient(135deg, #42b883 0%, #35495e 100%);
  color: white;
  padding: 12px 20px;
  border-bottom: 1px solid #eaeaea;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.panel-header h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
}

.toggle-button {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 6px;
  color: white;
  cursor: pointer;
  padding: 4px;
  font-size: 12px;
  font-weight: bold;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 36px;
}

.toggle-button:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.1);
}

.toggle-button:active {
  transform: scale(0.95);
}

.code-editor {
  flex: 1;
  overflow: auto;
  margin: 0;
  padding: 0;
  background: #f6f8fa;
  font-family: 'Consolas', 'Cascadia Code', 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.3;
  text-align: left;
  border: none;
  outline: none;
  tab-size: 2;
}

.code-editor code {
  display: block;
  padding: 20px;
  white-space: pre;
  overflow-x: auto;
}

.preview-content {
  flex: 1;
  overflow: auto;
  padding: 20px;
  background: white;
}

.empty-state {
  text-align: center;
  padding: 80px 40px;
  color: #999;
  font-size: 1.1rem;
  margin-top: 40px;
}
</style>