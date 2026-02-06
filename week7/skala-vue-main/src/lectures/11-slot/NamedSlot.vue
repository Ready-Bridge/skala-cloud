<template>
  <header>
    <h4>헤더영역</h4>
    <slot name="header"></slot>
  </header>
  <main>
    <h4>메인영역</h4>
    <slot></slot>
  </main>
  <footer>
    <h4>푸터영역</h4>
    <slot name="footer"></slot>
  </footer>
</template>

<style scoped>
header {
  background-color: yellowgreen;
  padding: 12px;
  text-align: center;
}

main {
  min-height: 200px;
  padding: 20px;
  text-align: center;
}

footer {
  background-color: #f0f0f0;
  padding: 10px;
  text-align: center;
}
</style>