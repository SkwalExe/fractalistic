<script setup>
import DefaultTheme from 'vitepress/theme'
const { Layout } = DefaultTheme
</script>

<template>
  <div class="announcement-bar">
        ⚠️ Warning: Fractalistic is deprecated. Please use the new version, Rsfrac instead: <a href="https://rsfrac.skwal.net">OPEN THE NEW SITE</a>
  </div>
  <Layout>
  </Layout>
</template>

<style>
.announcement-bar {
  position: fixed;
  width: 100%;
  bottom: 0;
  left: 0;
  z-index: 10000;
  background: #fF4e0b;
  color: white;
  text-align: center;
  padding: 28px;
  font-weight: 500;
}
.announcement-bar a {
    color: black;
    background: red
}
</style>

