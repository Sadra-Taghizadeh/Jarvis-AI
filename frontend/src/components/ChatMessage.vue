<template>
  <div class="msg-row" :class="[message.role, { 'is-bg': message.isBackground }]">
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
        <span class="msg-time">{{ formatTime(message.timestamp) }}</span>
      </div>
      <div class="msg-bubble" :class="message.role">
        <div class="msg-text" v-html="renderedContent"></div>
      </div>
      <div class="msg-meta msg-meta-user" v-if="message.role === 'user'">
        <span class="msg-time">{{ formatTime(message.timestamp) }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  message: Object
})

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
  text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
  text = text.replace(/\*(.*?)\*/g, '<em>$1</em>')
  text = text.replace(/`(.*?)`/g, '<code>$1</code>')
  text = text.replace(/\n/g, '<br>')
  return text
})

function formatTime(date) {
  return new Date(date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
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
</style>
