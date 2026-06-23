<template>
  <button
    class="voice-btn"
    :class="{ listening: isListening }"
    @click="toggleListening"
    :title="isListening ? 'Stop listening' : 'Voice input'"
  >
    <div class="voice-ring" v-if="isListening"></div>
    <svg v-if="!isListening" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
      <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
      <line x1="12" y1="19" x2="12" y2="23"/>
      <line x1="8" y1="23" x2="16" y2="23"/>
    </svg>
    <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
      <rect x="6" y="6" width="12" height="12" rx="2"/>
    </svg>
  </button>
</template>

<script setup>
import { ref, onUnmounted } from 'vue'

const props = defineProps({ isListening: Boolean })
const emit = defineEmits(['voice-input'])
let recognition = null

function toggleListening() {
  props.isListening ? stopListening() : startListening()
}

function startListening() {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition
  if (!SR) { alert('Speech recognition not supported'); return }

  recognition = new SR()
  recognition.continuous = false
  recognition.interimResults = false
  recognition.lang = 'en-US'

  recognition.onresult = (e) => {
    emit('voice-input', e.results[0][0].transcript)
    stopListening()
  }
  recognition.onerror = () => stopListening()
  recognition.onend = () => stopListening()
  recognition.start()
}

function stopListening() {
  recognition?.stop()
  recognition = null
}

onUnmounted(() => stopListening())
</script>

<style scoped>
.voice-btn {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.03);
  color: #666;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.25s;
  position: relative;
  flex-shrink: 0;
}

.voice-btn:hover {
  background: rgba(0, 212, 255, 0.08);
  border-color: rgba(0, 212, 255, 0.2);
  color: #00d4ff;
}

.voice-btn.listening {
  background: rgba(0, 212, 255, 0.15);
  border-color: rgba(0, 212, 255, 0.4);
  color: #00d4ff;
}

.voice-ring {
  position: absolute;
  inset: -4px;
  border-radius: 16px;
  border: 2px solid rgba(0, 212, 255, 0.3);
  animation: pulse-ring 1.5s infinite;
}
</style>
