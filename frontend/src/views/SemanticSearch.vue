<script setup lang="ts">
import { ref, inject } from 'vue'
import type { Ref } from 'vue'

interface SearchItem {
  document: string
  key: string
  distance: number
  title: string
  publication: string
  pdf_key: string
}

const query = ref('')
const results = ref<SearchItem[]>([])
const loading = ref(false)
const error = ref<string | null>(null)
const selectedKeys = inject('selectedKeys') as Ref<string[]>

async function doSearch() {
  if (!query.value.trim()) {
    results.value = []
    return
  }

  loading.value = true
  error.value = null
  try {
    const res = await fetch('/api/semantic_search?n_results=40', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: [query.value], collections: selectedKeys.value }),
    })
    if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
    // semantic_search now returns items without title/publication/pdf_key
    const data = (await res.json()) as Array<{ document: string; key: string; distance: number }>
    // Show initial results immediately
    results.value = data.map(item => ({ ...item, title: '正在获取……', publication: '正在获取……', pdf_key: '' }))

    // For each item, fetch details asynchronously and merge into results
    for (const [i, item] of data.entries()) {
      fetch(`/api/item/${encodeURIComponent(item.key)}`)
        .then(async r => {
          if (!r.ok) throw new Error(`${r.status} ${r.statusText}`)
          const info = await r.json()
          // info = { title, pdf_key, publication }
          // Update the corresponding item in results
          results.value[i] = {
            ...results.value[i],
            title: info.title ?? '',
            publication: info.publication ?? '',
            pdf_key: info.pdf_key ?? '',
          }
        })
        .catch(() => {
          // If error, leave fields blank
        })
    }
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

    <div v-else class="results-grid">
      <div v-if="results.length === 0" class="no-results">未找到结果</div>
      <div v-for="item in results" :key="item.key" class="result-card">
        <div class="card-header">
          <div class="card-title">{{ item.title || '无标题' }}</div>
          <div class="card-meta">
            <span class="card-publication" v-if="item.publication">{{ item.publication }}</span>
            <span class="card-distance">距离: {{ item.distance.toFixed(3) }}</span>
          </div>
        </div>
        <div class="card-body">
          <div class="card-document">{{ item.document }}</div>
        </div>
        <div class="card-actions">
          <a :href="`zotero://select/library/items/${encodeURIComponent(item.key)}`" class="action-btn"
            title="在Zotero中查看">查看</a>
          <a v-if="item.pdf_key" href="###" @click.prevent="openItem(item.pdf_key)" class="action-btn"
            title="打开PDF">打开PDF</a>
        </div>
      </div>
    </div>
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
  padding: 0.6rem 1rem;
  border: 1.5px solid #b3d4fc;
  border-radius: 8px;
  font-size: 1.05rem;
  transition: border-color 0.2s, box-shadow 0.2s;
  outline: none;
  box-shadow: 0 1px 4px rgba(33, 118, 199, 0.07);
}

.search-box input:focus {
  border-color: #2176c7;
  box-shadow: 0 2px 8px rgba(33, 118, 199, 0.13);
}

.search-box button {
  padding: 0.32rem 0.8rem;
  border-radius: 5px;
  background: linear-gradient(90deg, #eaf6ff 0%, #f7fbff 100%);
  color: #2176c7;
  font-size: 0.97rem;
  font-weight: 500;
  border: 1px solid #cbe7ff;
  box-shadow: none;
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
}

.search-box button:disabled {
  background: #eaf6ff;
  color: #888;
  cursor: not-allowed;
  border-color: #eaf6ff;
  box-shadow: none;
}

.search-box button:hover:not(:disabled) {
  background: linear-gradient(90deg, #d0eaff 0%, #eaf6ff 100%);
  color: #174a7c;
  border-color: #90cdf4;
}

.loading,
.error,
.no-results {
  color: #666;
}

.error {
  color: #a33
}

.results-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.2rem;
  margin-top: 1rem;
}

.result-card {
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  padding: 1.1rem 1.2rem 0.8rem 1.2rem;
  transition: box-shadow 0.2s;
}

.result-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  border-color: #b3d4fc;
}

.card-header {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  margin-bottom: 0.5rem;
}

.card-title {
  font-size: 1.15rem;
  font-weight: 700;
  color: #1a2a3a;
  margin-bottom: 0.1rem;
  word-break: break-all;
}

.card-meta {
  display: flex;
  gap: 1.2rem;
  font-size: 0.92rem;
  color: #4a5a6a;
  align-items: center;
}

.card-publication {
  background: #eaf6ff;
  color: #2176c7;
  padding: 0.08rem 0.5rem;
  border-radius: 6px;
  font-size: 0.88rem;
}

.card-distance {
  font-size: 0.85rem;
  color: #888;
}

.card-body {
  margin-bottom: 0.7rem;
}

.card-document {
  font-size: 0.97rem;
  color: #222;
  opacity: 0.96;
  line-height: 1.7;
  word-break: break-word;
  max-height: calc(1.7em * 10);
  /* 10 lines */
  overflow: hidden;
  position: relative;
  transition: max-height 0.2s;
}

.card-document::after {
  content: '...';
  position: absolute;
  right: 0;
  bottom: 0;
  background: linear-gradient(90deg, rgba(255, 255, 255, 0) 0%, #fff 80%);
  padding-left: 1em;
  font-weight: bold;
  color: #888;
  display: block;
}

.card-actions {
  display: flex;
  gap: 0.7rem;
  margin-top: 0.2rem;
}

.action-btn {
  display: inline-block;
  padding: 0.32rem 0.8rem;
  border-radius: 5px;
  background: linear-gradient(90deg, #eaf6ff 0%, #f7fbff 100%);
  color: #2176c7;
  text-decoration: none;
  font-size: 0.97rem;
  font-weight: 500;
  border: 1px solid #cbe7ff;
  transition: background 0.2s, color 0.2s;
}

.action-btn:hover {
  background: linear-gradient(90deg, #d0eaff 0%, #eaf6ff 100%);
  color: #174a7c;
  border-color: #90cdf4;
}

.no-results {
  grid-column: 1/-1;
  text-align: center;
  color: #888;
  font-size: 1.05rem;
  padding: 1.5rem 0;
}
</style>
