<template>
  <div class="jarvis-app">
    <div class="bg-grid"></div>
    <div class="bg-glow"></div>

    <header class="app-header">
      <div class="header-left">
        <div class="logo">
          <div class="logo-ring" :class="connectionStatus">
            <div class="logo-core">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                <path d="M2 17l10 5 10-5"/>
                <path d="M2 12l10 5 10-5"/>
              </svg>
            </div>
          </div>
          <div class="logo-text">
            <h1>JARVIS</h1>
            <span class="version">v1.0</span>
          </div>
        </div>
      </div>

      <div class="header-center">
        <div class="status-pill" :class="connectionStatus">
          <span class="status-dot"></span>
          <span>{{ connectionStatusText }}</span>
        </div>
      </div>

      <div class="header-right">
        <button class="icon-btn" @click="clearChat" title="Clear chat">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/>
            <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/>
          </svg>
        </button>
        <div class="window-controls" v-if="isElectron">
          <button class="win-btn" @click="minimizeWindow">
            <svg width="12" height="12" viewBox="0 0 12 12"><rect y="5" width="12" height="1" fill="currentColor"/></svg>
          </button>
          <button class="win-btn" @click="maximizeWindow">
            <svg width="12" height="12" viewBox="0 0 12 12"><rect x="1" y="1" width="10" height="10" rx="1" fill="none" stroke="currentColor" stroke-width="1.2"/></svg>
          </button>
          <button class="win-btn close" @click="closeWindow">
            <svg width="12" height="12" viewBox="0 0 12 12"><path d="M1 1l10 10M11 1L1 11" stroke="currentColor" stroke-width="1.2"/></svg>
          </button>
        </div>
      </div>
    </header>

    <main class="chat-container" ref="chatContainer">
      <div class="chat-messages">
        <TransitionGroup name="msg">
          <ChatMessage
            v-for="(msg, index) in messages"
            :key="msg.timestamp.getTime()"
            :message="msg"
          />
        </TransitionGroup>

        <div v-if="isTyping" class="typing-wrapper">
          <div class="typing-avatar">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 2L2 7l10 5 10-5-10-5z"/>
              <path d="M2 17l10 5 10-5"/>
              <path d="M2 12l10 5 10-5"/>
            </svg>
          </div>
          <div class="typing-dots">
            <span></span><span></span><span></span>
          </div>
        </div>
      </div>
    </main>

    <footer class="app-footer">
      <div class="input-wrapper">
        <VoiceButton
          @voice-input="handleVoiceInput"
          :is-listening="isListening"
        />
        <input
          ref="inputField"
          v-model="inputText"
          @keydown.enter="sendMessage"
          placeholder="Ask Jarvis anything..."
          class="chat-input"
          :disabled="!isConnected"
        />
        <button
          @click="sendMessage"
          class="send-btn"
          :class="{ active: inputText.trim() }"
          :disabled="!inputText.trim() || !isConnected"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22 2L11 13"/>
            <path d="M22 2L15 22L11 13L2 9L22 2Z"/>
          </svg>
        </button>
      </div>
      <div class="footer-hint">
        Press <kbd>Enter</kbd> to send &middot; <kbd>Ctrl+Shift+J</kbd> to focus
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import ChatMessage from './components/ChatMessage.vue'
import VoiceButton from './components/VoiceButton.vue'

const inputText = ref('')
const messages = ref([])
const isTyping = ref(false)
const isListening = ref(false)
const isConnected = ref(false)
const connectionStatus = ref('disconnected')
const connectionStatusText = ref('Disconnected')
const isElectron = ref(typeof window !== 'undefined' && window.process && window.process.type === 'electron')
const chatContainer = ref(null)
const inputField = ref(null)

let ws = null
let reconnectTimer = null
let welcomeShown = false

onMounted(() => {
  connectWebSocket()
  if ('Notification' in window && Notification.permission === 'default') {
    Notification.requestPermission()
  }
})

onUnmounted(() => {
  if (reconnectTimer) clearTimeout(reconnectTimer)
  if (ws) ws.close()
})

function connectWebSocket() {
  if (ws && (ws.readyState === WebSocket.CONNECTING || ws.readyState === WebSocket.OPEN)) return

  ws = new WebSocket('ws://localhost:8765')

  ws.onopen = () => {
    isConnected.value = true
    connectionStatus.value = 'connected'
    connectionStatusText.value = 'Online'
    if (!welcomeShown) {
      welcomeShown = true
      messages.value.push({
        role: 'assistant',
        content: 'Hello! I am **Jarvis**, your AI assistant. I can control your computer, search the web, remember things, and more. How can I help?',
        timestamp: new Date()
      })
    }
  }

  ws.onmessage = (event) => {
    try {
      handleServerMessage(JSON.parse(event.data))
    } catch (e) {
      console.error('[WS] Parse error:', e)
    }
  }

  ws.onclose = () => {
    isConnected.value = false
    connectionStatus.value = 'disconnected'
    connectionStatusText.value = 'Offline'
    reconnectTimer = setTimeout(connectWebSocket, 3000)
  }

  ws.onerror = () => {
    connectionStatus.value = 'error'
    connectionStatusText.value = 'Error'
  }
}

function handleServerMessage(data) {
  isTyping.value = false

  if (data.type === 'status') return

  const scrollDown = () => {
    nextTick(() => {
      if (chatContainer.value) {
        chatContainer.value.scrollTop = chatContainer.value.scrollHeight
      }
    })
  }

  if (data.type === 'response') {
    const isBg = data.background === true
    messages.value.push({
      role: isBg ? 'notification' : 'assistant',
      content: data.message,
      timestamp: new Date(),
      isBackground: isBg
    })
    scrollDown()
    if (isBg && Notification.permission === 'granted') {
      new Notification('Jarvis', { body: data.message.substring(0, 200) })
    }
  } else if (data.type === 'reminder') {
    messages.value.push({
      role: 'reminder',
      content: data.message,
      timestamp: new Date()
    })
    scrollDown()
    if (Notification.permission === 'granted') {
      new Notification('Jarvis Reminder', { body: data.message })
    }
  } else if (data.type === 'action_result') {
    const r = data.result
    let display = r.analysis || r.message || (r.facts ? r.facts.map(f => `${f.key}: ${f.value}`).join('\n') : '') || (r.success ? 'Done' : `Error: ${r.error}`)
    messages.value.push({ role: 'system', content: display, timestamp: new Date() })
    scrollDown()
  } else if (data.type === 'error') {
    messages.value.push({ role: 'error', content: data.message, timestamp: new Date() })
    scrollDown()
  }
}

function sendMessage() {
  if (!inputText.value.trim() || !ws || ws.readyState !== WebSocket.OPEN) return

  messages.value.push({
    role: 'user',
    content: inputText.value,
    timestamp: new Date()
  })

  ws.send(JSON.stringify({ type: 'chat', content: inputText.value }))
  inputText.value = ''
  isTyping.value = true
}

function clearChat() {
  messages.value = []
}

function handleVoiceInput(transcript) {
  inputText.value = transcript
  sendMessage()
}

function minimizeWindow() { window.require?.('electron')?.remote?.getCurrentWindow()?.minimize() }
function maximizeWindow() { const w = window.require?.('electron')?.remote?.getCurrentWindow(); w && (w.isMaximized() ? w.unmaximize() : w.maximize()) }
function closeWindow() { window.require?.('electron')?.remote?.getCurrentWindow()?.hide() }
</script>

<style scoped>
.jarvis-app {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #08090d;
  color: #e0e0e0;
  position: relative;
  overflow: hidden;
}

.bg-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(0, 212, 255, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 212, 255, 0.03) 1px, transparent 1px);
  background-size: 60px 60px;
  pointer-events: none;
}

.bg-glow {
  position: absolute;
  top: -200px;
  left: 50%;
  transform: translateX(-50%);
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, rgba(0, 102, 255, 0.08) 0%, transparent 70%);
  pointer-events: none;
}

.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  background: rgba(10, 11, 16, 0.8);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  -webkit-app-region: drag;
  position: relative;
  z-index: 10;
}

.header-left, .header-center, .header-right {
  display: flex;
  align-items: center;
}

.header-left { flex: 1; }
.header-center { flex: 0; }
.header-right { flex: 1; justify-content: flex-end; gap: 8px; }

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-ring {
  width: 38px;
  height: 38px;
  border-radius: 12px;
  background: linear-gradient(135deg, rgba(0, 102, 255, 0.2), rgba(0, 212, 255, 0.2));
  border: 1px solid rgba(0, 212, 255, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  transition: all 0.3s;
}

.logo-ring.connected {
  border-color: rgba(0, 255, 136, 0.4);
  background: linear-gradient(135deg, rgba(0, 255, 136, 0.1), rgba(0, 212, 255, 0.1));
}

.logo-ring.connected::before {
  content: '';
  position: absolute;
  inset: -2px;
  border-radius: 14px;
  background: linear-gradient(135deg, #00ff88, #00d4ff);
  opacity: 0.15;
  animation: pulse-ring 2s infinite;
}

.logo-core {
  color: #00d4ff;
}

.logo-text h1 {
  font-size: 18px;
  font-weight: 700;
  letter-spacing: 6px;
  background: linear-gradient(135deg, #ffffff, #00d4ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  line-height: 1;
}

.version {
  font-size: 10px;
  color: #555;
  letter-spacing: 1px;
}

.status-pill {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 0.5px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.status-pill.connected {
  color: #00ff88;
  border-color: rgba(0, 255, 136, 0.2);
}

.status-pill.disconnected { color: #ff4444; }
.status-pill.error { color: #ffaa00; }

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
}

.status-pill.connected .status-dot {
  box-shadow: 0 0 8px rgba(0, 255, 136, 0.6);
  animation: dot-pulse 2s infinite;
}

@keyframes dot-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.icon-btn {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 8px;
  background: transparent;
  color: #666;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  -webkit-app-region: no-drag;
}

.icon-btn:hover {
  background: rgba(255, 255, 255, 0.05);
  color: #fff;
}

.window-controls {
  display: flex;
  gap: 4px;
  -webkit-app-region: no-drag;
}

.win-btn {
  width: 28px;
  height: 28px;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: #555;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
}

.win-btn:hover { background: rgba(255, 255, 255, 0.08); color: #fff; }
.win-btn.close:hover { background: #e81123; color: white; }

.chat-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px 24px;
  position: relative;
  z-index: 1;
}

.chat-messages {
  max-width: 780px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.typing-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 0;
  animation: slideUp 0.3s ease;
}

.typing-avatar {
  width: 32px;
  height: 32px;
  border-radius: 10px;
  background: linear-gradient(135deg, rgba(0, 102, 255, 0.3), rgba(0, 212, 255, 0.3));
  border: 1px solid rgba(0, 212, 255, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #00d4ff;
  flex-shrink: 0;
}

.typing-dots {
  display: flex;
  gap: 4px;
  padding: 10px 16px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 12px;
}

.typing-dots span {
  width: 6px;
  height: 6px;
  background: #00d4ff;
  border-radius: 50%;
  animation: typing-bounce 1.4s infinite ease-in-out;
}

.typing-dots span:nth-child(2) { animation-delay: 0.2s; }
.typing-dots span:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing-bounce {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.3; }
  40% { transform: scale(1); opacity: 1; }
}

.app-footer {
  padding: 12px 24px 8px;
  background: rgba(10, 11, 16, 0.6);
  backdrop-filter: blur(20px);
  border-top: 1px solid rgba(255, 255, 255, 0.04);
  position: relative;
  z-index: 10;
}

.input-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
  max-width: 780px;
  margin: 0 auto;
  padding: 6px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  transition: border-color 0.3s, box-shadow 0.3s;
}

.input-wrapper:focus-within {
  border-color: rgba(0, 212, 255, 0.3);
  box-shadow: 0 0 20px rgba(0, 212, 255, 0.05);
}

.chat-input {
  flex: 1;
  padding: 10px 4px;
  background: transparent;
  border: none;
  color: #e0e0e0;
  font-size: 14px;
  outline: none;
  font-family: inherit;
}

.chat-input::placeholder { color: #555; }

.send-btn {
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 12px;
  background: rgba(0, 102, 255, 0.15);
  color: #555;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.25s;
  flex-shrink: 0;
}

.send-btn.active {
  background: linear-gradient(135deg, #0066ff, #00d4ff);
  color: white;
  box-shadow: 0 4px 15px rgba(0, 102, 255, 0.3);
}

.send-btn.active:hover {
  transform: scale(1.05);
  box-shadow: 0 6px 20px rgba(0, 102, 255, 0.4);
}

.footer-hint {
  text-align: center;
  font-size: 11px;
  color: #444;
  padding: 6px 0 2px;
  max-width: 780px;
  margin: 0 auto;
}

.footer-hint kbd {
  padding: 1px 5px;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  font-family: inherit;
  font-size: 10px;
  color: #666;
}

.msg-enter-active { animation: slideUp 0.3s ease; }
</style>
