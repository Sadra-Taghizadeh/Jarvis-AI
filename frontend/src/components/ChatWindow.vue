<template>
  <div class="chat-window" ref="chatContainer">
    <div 
      v-for="(msg, index) in messages" 
      :key="index"
      class="message"
      :class="msg.role"
    >
      <div class="message-avatar">
        <span v-if="msg.role === 'user'">U</span>
        <span v-else-if="msg.role === 'assistant'">J</span>
        <span v-else-if="msg.role === 'reminder'">!</span>
        <span v-else>S</span>
      </div>
      <div class="message-content">
        <div class="message-text">{{ msg.content }}</div>
        <div class="message-time">{{ formatTime(msg.timestamp) }}</div>
      </div>
    </div>

    <div v-if="isTyping" class="message assistant">
      <div class="message-avatar"><span>J</span></div>
      <div class="message-content">
        <div class="typing-indicator">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'

const props = defineProps({
  messages: Array,
  isTyping: Boolean
})

const chatContainer = ref(null)

watch(() => props.messages.length, async () => {
  await nextTick()
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
})

function formatTime(date) {
  return new Date(date).toLocaleTimeString([], { 
    hour: '2-digit', 
    minute: '2-digit' 
  })
}
</script>

<style scoped>
.chat-window {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-width: 800px;
  margin: 0 auto;
}

.message {
  display: flex;
  gap: 12px;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 14px;
  flex-shrink: 0;
}

.message.user .message-avatar {
  background: #0066ff;
}

.message.assistant .message-avatar {
  background: linear-gradient(135deg, #00d4ff, #0066ff);
}

.message.notification .message-avatar {
  background: linear-gradient(135deg, #00ff88, #00cc66);
  animation: glow 2s infinite;
}

@keyframes glow {
  0%, 100% { box-shadow: 0 0 5px rgba(0, 255, 136, 0.5); }
  50% { box-shadow: 0 0 20px rgba(0, 255, 136, 0.8); }
}

.message.notification .message-text {
  background: rgba(0, 255, 136, 0.1);
  border: 1px solid rgba(0, 255, 136, 0.3);
  color: #00ff88;
}

.message.system .message-avatar {
  background: #00ff88;
}

.message.error .message-avatar {
  background: #ff4444;
}

.message.reminder .message-avatar {
  background: #ffaa00;
}

.message.reminder .message-text {
  background: rgba(255, 170, 0, 0.1);
  border: 1px solid rgba(255, 170, 0, 0.3);
  color: #ffaa00;
}

.message-content {
  max-width: 70%;
}

.message-text {
  padding: 12px 16px;
  border-radius: 12px;
  line-height: 1.5;
  font-size: 14px;
}

.message.user .message-text {
  background: #0066ff;
  color: white;
  border-bottom-right-radius: 4px;
}

.message.assistant .message-text {
  background: #1a1a2e;
  border-bottom-left-radius: 4px;
}

.message.system .message-text {
  background: rgba(0, 255, 136, 0.1);
  border: 1px solid rgba(0, 255, 136, 0.3);
  color: #00ff88;
}

.message.error .message-text {
  background: rgba(255, 68, 68, 0.1);
  border: 1px solid rgba(255, 68, 68, 0.3);
  color: #ff4444;
}

.message-time {
  font-size: 11px;
  color: #666;
  margin-top: 4px;
}

.message.user .message-time {
  text-align: right;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 12px 16px;
  background: #1a1a2e;
  border-radius: 12px;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: #00d4ff;
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) { animation-delay: 0s; }
.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.5; }
  40% { transform: scale(1); opacity: 1; }
}
</style>
