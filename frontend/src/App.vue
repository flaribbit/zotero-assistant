<script setup lang="ts">
import { RouterView, RouterLink } from 'vue-router'
import { ref, onMounted } from 'vue'

interface Collection {
  key: string
  name: string
  numItems: number
}

const collections = ref<Collection[]>([])
const selectedKeys = ref<string[]>([])
const loading = ref(false)
const error = ref<string | null>(null)

async function loadCollections() {
  loading.value = true
  error.value = null
  try {
    const res = await fetch('/api/collections')
    if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
    const data = (await res.json()) as Collection[]
    collections.value = data
  } catch (err: any) {
    error.value = err?.message ?? String(err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadCollections()
})
</script>

<template>
  <div class="app-layout">
    <aside class="sidebar">
      <div class="collections">
        <div class="collections-head">
          <h3>Collections</h3>
          <div class="toolbar">
            <button type="button" @click="selectedKeys = collections.map(c => c.key)">全选</button>
            <button type="button" @click="selectedKeys = []">清除</button>
          </div>
        </div>

        <div v-if="loading" class="loading">加载中…</div>
        <div v-else-if="error" class="error">加载失败：{{ error }}</div>

        <ul v-else class="collection-list">
          <li v-for="col in collections" :key="col.key" class="collection-item">
            <label class="collection-label" :title="col.name">
              <input class="collection-checkbox" type="checkbox" :value="col.key" v-model="selectedKeys" />
              <span class="col-name">{{ col.name }}</span>
              <span class="col-count" aria-hidden="true">{{ col.numItems }}</span>
            </label>
          </li>
        </ul>

        <div class="selection-summary">
          已选: <strong>{{ selectedKeys.length }}</strong> / {{ collections.length }}
        </div>
      </div>
    </aside>

    <section class="main-area">
      <header class="top-nav">
        <!-- top nav for switching routes as requested -->
        <nav>
          <ul>
            <li>
              <RouterLink to="/">主页</RouterLink>
            </li>
            <li>
              <RouterLink to="/fulltext">全文搜索</RouterLink>
            </li>
            <li>
              <RouterLink to="/semantic">语义搜索</RouterLink>
            </li>
            <li>
              <RouterLink to="/llm">LLM问答</RouterLink>
            </li>
          </ul>
        </nav>
      </header>

      <main class="content">
        <!-- nested routes render here -->
        <RouterView />
      </main>
    </section>
  </div>
</template>

<style>
body {
  margin: 0;
}

/* Layout for App: left sidebar, top navigation in main area, and scrollable main content */
.app-layout {
  display: grid;
  grid-template-columns: 240px 1fr;
  /* sidebar + main */
  grid-template-rows: 1fr;
  gap: 1rem;
  height: 100vh;
  /* full viewport so content can scroll internally */
}

.sidebar {
  background: rgba(0, 0, 0, 0.03);
  padding: 8px;
  border-right: 1px solid rgba(0, 0, 0, 0.06);
  overflow: auto;
  /* allow sidebar to scroll if content grows */
}

.main-area {
  display: flex;
  flex-direction: column;
  min-height: 0;
  /* allow children with overflow to behave correctly */
}

.top-nav {
  background: transparent;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  padding: 0.5rem 1rem;
  flex: 0 0 auto;
}

.top-nav nav ul {
  display: flex;
  gap: 1rem;
  margin: 0;
  padding: 0;
  list-style: none;
  align-items: center;
}

.content {
  padding: 1rem;
  overflow: auto;
  /* scroll content inside main-area */
  flex: 1 1 0%;
  min-height: 0;
  /* required for correct scrolling in flex containers */
}

/* Collections list styles */
.collections {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.collections-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.5rem;
}

.collections h3 {
  margin: 0;
  font-size: 1rem;
}

.toolbar button {
  background: transparent;
  border: 1px solid rgba(0, 0, 0, 0.08);
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  font-size: 0.85rem;
  cursor: pointer;
}

.toolbar button:hover {
  background: rgba(0, 0, 0, 0.03);
}

.loading {
  color: #666;
  padding: 0.5rem 0;
}

.error {
  color: #a33;
  padding: 0.5rem 0;
}

.collection-list {
  margin: 0;
  padding: 0.25rem 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.collection-item {
  border-radius: 6px;
}

.collection-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.4rem 0.5rem;
  cursor: pointer;
  user-select: none;
}

.collection-label:hover {
  background: rgba(0, 0, 0, 0.02);
}

.collection-checkbox {
  width: 16px;
  height: 16px;
}

.col-name {
  flex: 1 1 auto;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.col-count {
  background: rgba(0, 0, 0, 0.06);
  color: #333;
  padding: 0.08rem 0.4rem;
  border-radius: 999px;
  font-size: 0.75rem;
  min-width: 28px;
  text-align: center;
}

.selection-summary {
  margin-top: 0.5rem;
  font-size: 0.85rem;
  color: #444;
}

/* Responsive: stack sidebar above main on small screens */
@media (max-width: 768px) {
  .app-layout {
    grid-template-columns: 1fr;
    grid-auto-rows: auto 1fr;
    height: auto;
  }

  .sidebar {
    border-right: none;
    border-bottom: 1px solid rgba(0, 0, 0, 0.06);
    width: 100%;
  }

  .top-nav nav ul {
    flex-wrap: wrap;
    gap: 0.5rem;
  }
}
</style>
