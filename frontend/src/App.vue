<template>
  <div class="jarvis-app" :class="{ 'dark-mode': isDarkMode }">
    <header class="app-header" data-tauri-drag-region>
      <div class="logo">
        <span class="logo-icon">J</span>
        <h1>JARVIS</h1>
      </div>
      <div class="status" :class="connectionStatus">
        <span class="status-dot"></span>
        {{ connectionStatusText }}
      </div>
      <div class="window-controls" v-if="isElectron">
        <button class="win-btn minimize" @click="minimizeWindow">−</button>
        <button class="win-btn maximize" @click="maximizeWindow">□</button>
        <button class="win-btn close" @click="closeWindow">×</button>
      </div>
    </header>

    <main class="chat-container">
      <ChatWindow 
        :messages="messages" 
        :is-typing="isTyping"
        @send="sendMessage"
      />
    </main>

    <footer class="app-footer">
      <VoiceButton 
        @voice-input="handleVoiceInput"
        :is-listening="isListening"
      />
      <input 
        v-model="inputText"
        @keyup.enter="sendMessage"
        placeholder="Type a command or ask anything..."
        class="chat-input"
      />
      <button @click="sendMessage" class="send-btn">
        Send
      </button>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import ChatWindow from './components/ChatWindow.vue'
import VoiceButton from './components/VoiceButton.vue'
import { useJarvisStore } from './stores/jarvis'

const store = useJarvisStore()

const inputText = ref('')
const messages = ref([])
const isTyping = ref(false)
const isListening = ref(false)
const isDarkMode = ref(true)
const connectionStatus = ref('disconnected')
const connectionStatusText = ref('Disconnected')
const isElectron = ref(typeof window !== 'undefined' && window.process && window.process.type === 'electron')

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
  if (ws && (ws.readyState === WebSocket.CONNECTING || ws.readyState === WebSocket.OPEN)) {
    console.log('[WS] Already connected/connecting, skipping')
    return
  }

  console.log('[WS] Connecting to ws://localhost:8765...')
  ws = new WebSocket('ws://localhost:8765')

  ws.onopen = () => {
    console.log('[WS] Connected!')
    connectionStatus.value = 'connected'
    connectionStatusText.value = 'Connected'
    if (!welcomeShown) {
      welcomeShown = true
      messages.value.push({
        role: 'assistant',
        content: 'Hello! I am Jarvis. How can I help you today?',
        timestamp: new Date()
      })
    }
  }

  ws.onmessage = (event) => {
    console.log('[WS] Received:', event.data.substring(0, 200))
    try {
      const data = JSON.parse(event.data)
      handleServerMessage(data)
    } catch (e) {
      console.error('[WS] Parse error:', e)
    }
  }

  ws.onclose = (event) => {
    console.log('[WS] Disconnected. Code:', event.code, 'Reason:', event.reason)
    connectionStatus.value = 'disconnected'
    connectionStatusText.value = 'Disconnected'
    reconnectTimer = setTimeout(connectWebSocket, 3000)
  }

  ws.onerror = (error) => {
    console.error('[WS] Error:', error)
    connectionStatus.value = 'error'
    connectionStatusText.value = 'Connection Error'
  }
}

function handleServerMessage(data) {
  console.log('[MSG] Type:', data.type, '| Data:', JSON.stringify(data).substring(0, 300))
  isTyping.value = false

  if (data.type === 'status') {
    console.log('[MSG] Status from server:', data.message)
    return
  } else if (data.type === 'response') {
    const isBackground = data.background === true
    messages.value.push({
      role: isBackground ? 'notification' : 'assistant',
      content: data.message,
      timestamp: new Date(),
      isBackground
    })

    if (isBackground && Notification.permission === 'granted') {
      new Notification('Jarvis', { body: data.message.substring(0, 200) })
    }

    if (isBackground) {
      const chatContainer = document.querySelector('.chat-container')
      if (chatContainer) chatContainer.scrollTop = chatContainer.scrollHeight
    }

  } else if (data.type === 'reminder') {
    messages.value.push({
      role: 'reminder',
      content: `Reminder: ${data.message}`,
      timestamp: new Date()
    })

    if (Notification.permission === 'granted') {
      new Notification('Jarvis Reminder', { body: data.message })
    }

  } else if (data.type === 'action_result') {
    const result = data.result
    let display = ''

    if (result.analysis) {
      display = result.analysis
    } else if (result.facts) {
      display = result.facts.map(f => `${f.key}: ${f.value}`).join('\n')
    } else if (result.reminders) {
      if (result.reminders.length === 0) {
        display = 'No pending reminders'
      } else {
        display = result.reminders.map(r => `${r.message} at ${r.remind_at}`).join('\n')
      }
    } else if (result.success) {
      display = result.message || 'Done'
    } else {
      display = `Error: ${result.error}`
    }

    messages.value.push({
      role: 'system',
      content: display,
      timestamp: new Date()
    })
  } else if (data.type === 'error') {
    messages.value.push({
      role: 'error',
      content: data.message,
      timestamp: new Date()
    })
  } else {
    console.log('[MSG] Unknown type:', data.type)
  }
}

function sendMessage() {
  if (!inputText.value.trim()) {
    console.log('[SEND] Empty message, skipping')
    return
  }

  if (!ws || ws.readyState !== WebSocket.OPEN) {
    console.error('[SEND] WebSocket not open! State:', ws?.readyState)
    return
  }

  console.log('[SEND] Sending:', inputText.value)
  messages.value.push({
    role: 'user',
    content: inputText.value,
    timestamp: new Date()
  })

  ws.send(JSON.stringify({
    type: 'chat',
    content: inputText.value
  }))
  console.log('[SEND] Message sent')

  inputText.value = ''
  isTyping.value = true
}

function handleVoiceInput(transcript) {
  inputText.value = transcript
  sendMessage()
}

function minimizeWindow() {
  if (window.require) {
    const { remote } = window.require('electron')
    if (remote) remote.getCurrentWindow().minimize()
  }
}

function maximizeWindow() {
  if (window.require) {
    const { remote } = window.require('electron')
    if (remote) {
      const win = remote.getCurrentWindow()
      win.isMaximized() ? win.unmaximize() : win.maximize()
    }
  }
}

function closeWindow() {
  if (window.require) {
    const { remote } = window.require('electron')
    if (remote) remote.getCurrentWindow().hide()
  }
}
</script>

<style scoped>
.jarvis-app {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #0a0a0f;
  color: #e0e0e0;
  font-family: 'Segoe UI', system-ui, sans-serif;
}

.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: #12121a;
  border-bottom: 1px solid #1e1e2e;
  -webkit-app-region: drag;
}

.window-controls {
  display: flex;
  gap: 8px;
  -webkit-app-region: no-drag;
}

.win-btn {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 8px;
  background: #1a1a2e;
  color: #888;
  font-size: 18px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.win-btn:hover {
  background: #2a2a3e;
  color: #fff;
}

.win-btn.close:hover {
  background: #ff4444;
  color: white;
}

.win-btn.minimize:hover {
  background: #ffaa00;
  color: white;
}

.win-btn.maximize:hover {
  background: #00ff88;
  color: white;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #00d4ff, #0066ff);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 20px;
}

.logo h1 {
  font-size: 24px;
  font-weight: 600;
  letter-spacing: 4px;
  background: linear-gradient(135deg, #00d4ff, #0066ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.status {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.status.connected .status-dot {
  background: #00ff88;
  box-shadow: 0 0 10px #00ff88;
}

.status.disconnected .status-dot {
  background: #ff4444;
}

.status.error .status-dot {
  background: #ffaa00;
}

.chat-container {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.app-footer {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 24px;
  background: #12121a;
  border-top: 1px solid #1e1e2e;
}

.chat-input {
  flex: 1;
  padding: 12px 16px;
  background: #1a1a2e;
  border: 1px solid #2a2a3e;
  border-radius: 8px;
  color: #e0e0e0;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}

.chat-input:focus {
  border-color: #00d4ff;
}

.send-btn {
  padding: 12px 24px;
  background: linear-gradient(135deg, #00d4ff, #0066ff);
  border: none;
  border-radius: 8px;
  color: white;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.send-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 212, 255, 0.3);
}
</style>
