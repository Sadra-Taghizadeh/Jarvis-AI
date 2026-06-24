import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

const STORAGE_KEY = 'jarvis_messages'

export const useJarvisStore = defineStore('jarvis', () => {
  const messages = ref([])
  const isConnected = ref(false)
  const isTyping = ref(false)
  const connectionStatus = ref('disconnected')
  const connectionStatusText = ref('Disconnected')

  function loadFromStorage() {
    try {
      const stored = localStorage.getItem(STORAGE_KEY)
      if (stored) {
        const parsed = JSON.parse(stored)
        messages.value = parsed.map(m => ({
          ...m,
          timestamp: new Date(m.timestamp)
        }))
      }
    } catch (e) {
      console.warn('[Store] Failed to load messages from storage:', e)
    }
  }

  function saveToStorage() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(messages.value))
    } catch (e) {
      console.warn('[Store] Failed to save messages to storage:', e)
    }
  }

  function addMessage(message) {
    messages.value.push({
      ...message,
      timestamp: new Date()
    })
    saveToStorage()
  }

  function updateLastMessage(content) {
    if (messages.value.length > 0) {
      messages.value[messages.value.length - 1].content = content
      saveToStorage()
    }
  }

  function removeMessage(id) {
    const idx = messages.value.findIndex(m => m.timestamp.getTime() === id)
    if (idx !== -1) {
      messages.value.splice(idx, 1)
      saveToStorage()
    }
  }

  function clearMessages() {
    messages.value = []
    saveToStorage()
  }

  loadFromStorage()

  return {
    messages,
    isConnected,
    isTyping,
    connectionStatus,
    connectionStatusText,
    addMessage,
    updateLastMessage,
    removeMessage,
    clearMessages
  }
})
