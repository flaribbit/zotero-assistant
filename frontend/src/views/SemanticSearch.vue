<script setup lang="ts">
import { ref } from 'vue'

interface SearchItem {
  document: string
  key: string
  distance: number
  title: string
  publication: string
}

const query = ref('')
const results = ref<SearchItem[]>([])
const loading = ref(false)
const error = ref<string | null>(null)

async function doSearch() {
  if (!query.value.trim()) {
    results.value = []
    return
  }

  loading.value = true
  error.value = null
  try {
    const res = await fetch('/api/semantic_search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify([query.value]),
    })
    if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
    const data = (await res.json()) as SearchItem[]
    results.value = data
  } catch (err: any) {
    error.value = err?.message ?? String(err)
  } finally {
    loading.value = false
  }
}

const openItem = (key: string) => {
  fetch(`/api/open/${encodeURIComponent(key)}`, { method: 'GET' })
}
</script>

<template>
  <div class="semantic-search">
    <h2>语义搜索</h2>

    <div class="search-box">
      <input v-model="query" @keyup.enter="doSearch" placeholder="输入查询并回车或点击搜索" aria-label="搜索查询" />
      <button type="button" @click="doSearch" :disabled="loading">搜索</button>
    </div>

    <div v-if="loading" class="loading">搜索中…</div>
    <div v-else-if="error" class="error">错误：{{ error }}</div>

    <ul v-else class="results">
      <li v-if="results.length === 0" class="no-results">未找到结果</li>
      <li v-for="item in results" :key="item.key" class="result-item">
        <div class="result-main">
          <div class="title">{{ item.title }}</div>
          <div class="publication">{{ item.publication }}</div>
        </div>

        <div class="result-side">
          <div class="distance">距离: {{ item.distance.toFixed(3) }}</div>
          <div class="actions">
            <a :href="`zotero://select/library/items/${encodeURIComponent(item.key)}`" class="button">查看</a>
            <a @click.prevent="openItem(item.key)" class="button">打开</a>
          </div>
        </div>

        <div class="document">{{ item.document }}</div>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.semantic-search {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.search-box {
  display: flex;
  gap: 0.5rem;
}

.search-box input {
  flex: 1 1 auto;
  padding: 0.5rem;
}

.search-box button {
  padding: 0.45rem 0.8rem;
}

.loading,
.error,
.no-results {
  color: #666;
}

.error {
  color: #a33
}

.results {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.result-item {
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 6px;
  padding: 0.6rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.result-main {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.title {
  font-weight: 600;
  font-size: 1.02rem;
}

.publication {
  color: #444;
  font-size: 0.95rem;
}

.document {
  font-size: 0.85rem;
  color: #333;
  opacity: 0.9;
}

.result-side {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.5rem;
}

.distance {
  font-size: 0.75rem;
  color: #666;
}

.actions .button {
  display: inline-block;
  padding: 0.28rem 0.5rem;
  border-radius: 4px;
  background: rgba(0, 0, 0, 0.04);
  color: inherit;
  text-decoration: none;
  font-size: 0.9rem;
  margin-left: 0.25rem;
}

.actions .button:hover {
  background: rgba(0, 0, 0, 0.06);
}

@media (min-width: 640px) {
  .result-item {
    flex-direction: row;
    align-items: flex-start;
  }

  .result-main {
    flex: 1 1 auto;
  }

  .result-side {
    flex: 0 0 160px;
    display: flex;
    flex-direction: column;
    align-items: flex-end;
  }

  .document {
    margin-top: 0.25rem;
  }
}
</style>
