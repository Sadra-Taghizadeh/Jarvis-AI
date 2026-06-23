<template>
  <button 
    class="voice-btn"
    :class="{ listening: isListening }"
    @click="toggleListening"
  >
    <svg v-if="!isListening" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
      <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
      <line x1="12" y1="19" x2="12" y2="23"></line>
      <line x1="8" y1="23" x2="16" y2="23"></line>
    </svg>
    <div v-else class="pulse-ring"></div>
  </button>
</template>

<script setup>
import { ref, onUnmounted } from 'vue'

const props = defineProps({
  isListening: Boolean
})

const emit = defineEmits(['voice-input'])

let recognition = null

function toggleListening() {
  if (props.isListening) {
    stopListening()
  } else {
    startListening()
  }
}

function startListening() {
  if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
    alert('Speech recognition not supported in this browser')
    return
  }

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
  recognition = new SpeechRecognition()
  recognition.continuous = false
  recognition.interimResults = false
  recognition.lang = 'en-US'

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript
    emit('voice-input', transcript)
    stopListening()
  }

  recognition.onerror = (event) => {
    console.error('Speech recognition error:', event.error)
    stopListening()
  }

  recognition.onend = () => {
    stopListening()
  }

  recognition.start()
}

function stopListening() {
  if (recognition) {
    recognition.stop()
    recognition = null
  }
}

onUnmounted(() => {
  stopListening()
})
</script>

<style scoped>
.voice-btn {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  border: none;
  background: #1a1a2e;
  color: #00d4ff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  position: relative;
}

.voice-btn:hover {
  background: #2a2a3e;
  transform: scale(1.05);
}

.voice-btn.listening {
  background: rgba(0, 212, 255, 0.2);
}

.pulse-ring {
  width: 20px;
  height: 20px;
  background: #00d4ff;
  border-radius: 50%;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% { transform: scale(0.8); opacity: 1; }
  100% { transform: scale(1.5); opacity: 0; }
}
</style>
