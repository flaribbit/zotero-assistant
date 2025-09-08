<script setup lang="ts">
import { ref } from 'vue'

const userInput = ref('')
const llmResponse = ref('')
const augmentedPrompt = ref('')
const loading = ref(false)
const statusMessage = ref('')

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
      method: 'POST'
    })
    if (!promptRes.ok) statusMessage.value = `Error fetching prompt: ${promptRes.status} ${promptRes.statusText}`
    augmentedPrompt.value = (await promptRes.json()).prompt

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
</script>

<template>
  <div>
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

      <div v-if="llmResponse" class="llm-response">
        <p>{{ llmResponse }}</p>
        <button @click="copyToClipboard(llmResponse)">复制回答</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.input-section {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

textarea {
  width: 100%;
  padding: 0.6rem;
  border: 1.5px solid #b3d4fc;
  border-radius: 8px;
  font-size: 1rem;
  resize: vertical;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
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
  white-space: pre-wrap;
  word-wrap: break-word;
}

.augmented-prompt,
.llm-response {
  margin-top: 1rem;
}

.augmented-prompt button,
.llm-response button {
  margin-top: 0.5rem;
  padding: 0.4rem 0.8rem;
  font-size: 0.9rem;
  background: #eaf6ff;
  color: #2176c7;
  border: 1px solid #cbe7ff;
  border-radius: 5px;
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
}

.augmented-prompt button:hover,
.llm-response button:hover {
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
