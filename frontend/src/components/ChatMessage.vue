<template>
  <div class="msg-row" :class="[message.role, { 'is-bg': message.isBackground }]" @mouseenter="showActions = true" @mouseleave="showActions = false">
    <div class="msg-avatar" :class="message.role">
      <template v-if="message.role === 'user'">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
          <circle cx="12" cy="7" r="4"/>
        </svg>
      </template>
      <template v-else-if="message.role === 'assistant' || message.role === 'notification'">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 2L2 7l10 5 10-5-10-5z"/>
          <path d="M2 17l10 5 10-5"/>
          <path d="M2 12l10 5 10-5"/>
        </svg>
      </template>
      <template v-else-if="message.role === 'reminder'">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
          <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
        </svg>
      </template>
      <template v-else-if="message.role === 'error'">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/>
        </svg>
      </template>
      <template v-else>
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
          <polyline points="14 2 14 8 20 8"/>
        </svg>
      </template>
    </div>

    <div class="msg-body">
      <div class="msg-meta" v-if="message.role !== 'user'">
        <span class="msg-sender">{{ senderName }}</span>
        <span class="msg-time">{{ relativeTime }}</span>
        <div class="msg-actions" v-if="showActions">
          <button class="action-btn" @click="copyMessage" :title="copied ? 'Copied!' : 'Copy'">
            <svg v-if="!copied" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
            </svg>
            <svg v-else width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="20 6 9 17 4 12"/>
            </svg>
          </button>
          <button class="action-btn delete" @click="$emit('delete', message.timestamp.getTime())" title="Delete">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
            </svg>
          </button>
        </div>
      </div>
      <div class="msg-bubble" :class="message.role">
        <div class="msg-text" v-html="renderedContent"></div>
      </div>
      <div class="msg-meta msg-meta-user" v-if="message.role === 'user'">
        <span class="msg-time">{{ relativeTime }}</span>
        <div class="msg-actions" v-if="showActions">
          <button class="action-btn" @click="copyMessage" :title="copied ? 'Copied!' : 'Copy'">
            <svg v-if="!copied" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
            </svg>
            <svg v-else width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="20 6 9 17 4 12"/>
            </svg>
          </button>
          <button class="action-btn delete" @click="$emit('delete', message.timestamp.getTime())" title="Delete">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  message: Object
})

defineEmits(['delete'])

const showActions = ref(false)
const copied = ref(false)

const senderName = computed(() => {
  const names = {
    assistant: 'Jarvis',
    notification: 'Jarvis',
    system: 'System',
    reminder: 'Reminder',
    error: 'Error'
  }
  return names[props.message.role] || 'Jarvis'
})

const renderedContent = computed(() => {
  let text = props.message.content
  text = text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
  text = text.replace(/```(\w*)\n([\s\S]*?)```/g, '<pre><code class="lang-$1">$2</code></pre>')
  text = text.replace(/`([^`]+)`/g, '<code>$1</code>')
  text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
  text = text.replace(/\*(.*?)\*/g, '<em>$1</em>')
  text = text.replace(/^### (.+)$/gm, '<h3>$1</h3>')
  text = text.replace(/^## (.+)$/gm, '<h2>$1</h2>')
  text = text.replace(/^# (.+)$/gm, '<h1>$1</h1>')
  text = text.replace(/^- (.+)$/gm, '<li>$1</li>')
  text = text.replace(/(<li>.*<\/li>\n?)+/g, (match) => `<ul>${match}</ul>`)
  text = text.replace(/\n/g, '<br>')
  return text
})

const relativeTime = computed(() => {
  const now = Date.now()
  const msgTime = new Date(props.message.timestamp).getTime()
  const diff = now - msgTime

  if (diff < 60000) return 'just now'
  if (diff < 3600000) return `${Math.floor(diff / 60000)} min ago`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)} hours ago`
  if (diff < 604800000) return `${Math.floor(diff / 86400000)} days ago`
  return new Date(props.message.timestamp).toLocaleDateString()
})

async function copyMessage() {
  try {
    await navigator.clipboard.writeText(props.message.content)
    copied.value = true
    setTimeout(() => { copied.value = false }, 2000)
  } catch (e) {
    console.error('Copy failed:', e)
  }
}
</script>

<style scoped>
.msg-row {
  display: flex;
  gap: 10px;
  padding: 4px 0;
  animation: slideUp 0.3s ease;
}

.msg-row.user { flex-direction: row-reverse; }

.msg-avatar {
  width: 32px;
  height: 32px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.3s;
}

.msg-avatar.user {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  color: white;
}

.msg-avatar.assistant, .msg-avatar.notification {
  background: linear-gradient(135deg, rgba(0, 102, 255, 0.25), rgba(0, 212, 255, 0.25));
  border: 1px solid rgba(0, 212, 255, 0.3);
  color: #00d4ff;
}

.msg-avatar.notification {
  background: linear-gradient(135deg, rgba(0, 255, 136, 0.2), rgba(0, 212, 255, 0.2));
  border-color: rgba(0, 255, 136, 0.3);
  color: #00ff88;
  animation: glow 2s infinite;
}

@keyframes glow {
  0%, 100% { box-shadow: 0 0 5px rgba(0, 255, 136, 0.2); }
  50% { box-shadow: 0 0 15px rgba(0, 255, 136, 0.4); }
}

.msg-avatar.system {
  background: rgba(0, 255, 136, 0.15);
  border: 1px solid rgba(0, 255, 136, 0.25);
  color: #00ff88;
}

.msg-avatar.reminder {
  background: rgba(251, 191, 36, 0.15);
  border: 1px solid rgba(251, 191, 36, 0.25);
  color: #fbbf24;
}

.msg-avatar.error {
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.25);
  color: #ef4444;
}

.msg-body {
  max-width: 72%;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.msg-row.user .msg-body { align-items: flex-end; }

.msg-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 4px;
}

.msg-meta-user { justify-content: flex-end; }

.msg-sender {
  font-size: 12px;
  font-weight: 600;
  color: #888;
}

.msg-time {
  font-size: 11px;
  color: #444;
}

.msg-actions {
  display: flex;
  gap: 4px;
  opacity: 0;
  animation: fadeIn 0.15s ease forwards;
}

@keyframes fadeIn {
  to { opacity: 1; }
}

.action-btn {
  width: 24px;
  height: 24px;
  border: none;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.05);
  color: #666;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
}

.action-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}

.action-btn.delete:hover {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.msg-bubble {
  padding: 10px 14px;
  border-radius: 14px;
  line-height: 1.6;
  font-size: 13.5px;
  position: relative;
  word-wrap: break-word;
}

.msg-bubble.user {
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  color: white;
  border-bottom-right-radius: 4px;
}

.msg-bubble.assistant {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.06);
  color: #d0d0d0;
  border-bottom-left-radius: 4px;
}

.msg-bubble.notification {
  background: rgba(0, 255, 136, 0.06);
  border: 1px solid rgba(0, 255, 136, 0.15);
  color: #a0f0c0;
}

.msg-bubble.system {
  background: rgba(0, 255, 136, 0.06);
  border: 1px solid rgba(0, 255, 136, 0.15);
  color: #a0f0c0;
}

.msg-bubble.reminder {
  background: rgba(251, 191, 36, 0.06);
  border: 1px solid rgba(251, 191, 36, 0.15);
  color: #fde68a;
}

.msg-bubble.error {
  background: rgba(239, 68, 68, 0.06);
  border: 1px solid rgba(239, 68, 68, 0.15);
  color: #fca5a5;
}

.msg-text :deep(strong) { color: #fff; font-weight: 600; }
.msg-text :deep(em) { color: #00d4ff; }
.msg-text :deep(code) {
  background: rgba(0, 212, 255, 0.1);
  padding: 1px 5px;
  border-radius: 4px;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 12.5px;
  color: #00d4ff;
}
.msg-text :deep(pre) {
  background: rgba(0, 0, 0, 0.3);
  padding: 12px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 8px 0;
}
.msg-text :deep(pre code) {
  background: none;
  padding: 0;
  color: #e0e0e0;
}
.msg-text :deep(h1), .msg-text :deep(h2), .msg-text :deep(h3) {
  color: #fff;
  margin: 8px 0 4px;
}
.msg-text :deep(ul) {
  margin: 4px 0;
  padding-left: 20px;
}
.msg-text :deep(li) {
  margin: 2px 0;
}
</style>
