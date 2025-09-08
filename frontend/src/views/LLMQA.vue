<script setup lang="ts">
import { ref, inject } from 'vue'
import type { Ref } from 'vue'
import { marked } from 'marked'

const userInput = ref('')
const llmResponse = ref('')
const augmentedPrompt = ref('')
const loading = ref(false)
const statusMessage = ref('')
const dialogVisible = ref(false)
const dialogContent = ref({ title: '', publication: '', key: '', pdf_key: '', text: '' })
const selectedKeys = inject('selectedKeys') as Ref<string[]>

async function copyToClipboard(text: string) {
  try {
    await navigator.clipboard.writeText(text)
    alert('内容已复制到剪贴板')
  } catch (err) {
    alert('复制失败')
  }
}

async function sendQuery() {
  if (!userInput.value.trim()) return

  loading.value = true
  llmResponse.value = ''
  augmentedPrompt.value = ''
  statusMessage.value = '正在获取增强的 Prompt...'

  try {
    // Step 1: Fetch augmented prompt
    const promptRes = await fetch(`/api/get_full_prompt?query=${encodeURIComponent(userInput.value)}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(selectedKeys.value),
    })
    if (!promptRes.ok) statusMessage.value = `Error fetching prompt: ${promptRes.status} ${promptRes.statusText}`

    const promptData = await promptRes.json()
    augmentedPrompt.value = promptData.prompt

    // Step 2: Generate response
    statusMessage.value = '正在生成回答...'
    const res = await fetch('/api/completion', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify([{ role: 'user', content: augmentedPrompt.value }]),
    })

    if (!res.ok) statusMessage.value = `Error generating response: ${res.status} ${res.statusText}`

    const reader = res.body?.getReader()
    if (!reader) {
      statusMessage.value = 'Error: No response body'
      return
    }

    const decoder = new TextDecoder()
    let done = false

    while (!done) {
      const { value, done: readerDone } = await reader.read()
      done = readerDone
      const text = decoder.decode(value, { stream: true })
      llmResponse.value += text
    }
  } catch (err: any) {
    llmResponse.value = `Error: ${err.message}`
  } finally {
    loading.value = false
    statusMessage.value = ''
  }
}

async function handleLinkClick(key: string) {
  try {
    const res = await fetch(`/api/get_document?key=${encodeURIComponent(key)}`)
    if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)

    const data = await res.json()
    dialogContent.value = {
      title: data.title || '',
      publication: data.publication || '',
      key: data.key || '',
      pdf_key: data.pdf_key || '',
      text: data.text || ''
    }
    dialogVisible.value = true
  } catch (err) {
    const errorMessage = err instanceof Error ? err.message : String(err)
    alert(`Error fetching document: ${errorMessage}`)
  }
}

function renderMarkdownWithLinks(content: string) {
  // Replace [@key] with clickable spans
  const linkRegex = /\[@([A-Z0-9]{8}_\d+)]/g
  return marked(
    content.replace(linkRegex, (match, key) => {
      return `<span class='link' data-key='${key}'>${match}</span>`
    })
  )
}

function handleLinkClickEvent(event: MouseEvent) {
  const target = event.target as HTMLElement
  if (target.classList.contains('link')) {
    const key = target.getAttribute('data-key')
    if (key) {
      handleLinkClick(key)
    }
  }
}

function openItem(key: string) {
  fetch(`/api/open/${encodeURIComponent(key)}`, { method: 'GET' })
}
</script>

<template>
  <div class="llm-qa">
    <h2>LLM问答</h2>

    <div class="input-section">
      <textarea v-model="userInput" placeholder="输入您的问题..." rows="4"></textarea>
      <button @click="sendQuery" :disabled="loading">发送</button>
    </div>

    <div class="response-section">
      <p v-if="statusMessage">{{ statusMessage }}</p>

      <div v-if="augmentedPrompt" class="augmented-prompt">
        <p>{{ augmentedPrompt }}</p>
        <button @click="copyToClipboard(augmentedPrompt)">复制增强的 Prompt</button>
      </div>

      <div v-if="llmResponse" class="llm-response" v-html="renderMarkdownWithLinks(llmResponse)"
        @click="handleLinkClickEvent"></div>
      <button @click="copyToClipboard(llmResponse)">复制回答</button>
    </div>
  </div>

  <div v-if="dialogVisible" class="dialog-overlay">
    <div class="dialog">
      <h3>{{ dialogContent.title }}</h3>
      <p><strong>Publication:</strong> {{ dialogContent.publication }}</p>
      <p class="dialog-text">{{ dialogContent.text }}</p>
      <div class="dialog-actions">
        <a :href="`zotero://select/library/items/${encodeURIComponent(dialogContent.key)}`" class="action-btn"
          title="在Zotero中查看">查看</a>
        <button @click="openItem(dialogContent.pdf_key)" v-if="dialogContent.pdf_key">打开PDF</button>
      </div>
      <button @click="dialogVisible = false">关闭</button>
    </div>
  </div>
</template>


<style scoped>
.input-section {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
  box-sizing: border-box;
}

textarea {
  padding: 0.6rem;
  border: 1.5px solid #b3d4fc;
  border-radius: 8px;
  font-size: 1rem;
  resize: vertical;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
  box-sizing: border-box;
}

textarea:focus {
  border-color: #2176c7;
  box-shadow: 0 2px 8px rgba(33, 118, 199, 0.13);
}

button {
  align-self: flex-start;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  background: linear-gradient(90deg, #2176c7 0%, #90cdf4 100%);
  color: #fff;
  font-size: 1rem;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: background 0.2s, box-shadow 0.2s;
}

button:disabled {
  background: #eaf6ff;
  color: #888;
  cursor: not-allowed;
}

.response-section {
  margin-top: 1rem;
  padding: 1rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: #f9f9f9;
  word-wrap: break-word;
}

.augmented-prompt,
.llm-response {
  margin-top: 1rem;
}

.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}

.dialog {
  background: #fff;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
  width: 80%;
}

.dialog-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
}

.dialog-text {
  font-size: 0.9rem;
}

.action-btn {
  padding: 0.4rem 0.8rem;
  background: #eaf6ff;
  color: #2176c7;
  border: 1px solid #cbe7ff;
  border-radius: 5px;
  text-decoration: none;
  font-size: 0.9rem;
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
}

.action-btn:hover {
  background: #d0eaff;
  color: #174a7c;
}

.augmented-prompt p {
  font-size: 0.9rem;
  line-height: 1.4;
  max-height: calc(1.4em * 4);
  /* Limit to 4 lines */
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 4;
  /* Limit to 4 lines */
  -webkit-box-orient: vertical;
  line-clamp: 4;
  /* Standard property for compatibility */
}
</style>

<style>
.llm-qa .link {
  color: blue;
  text-decoration: underline;
  cursor: pointer;
}

.llm-qa .link:hover {
  color: darkblue;
}
</style>
