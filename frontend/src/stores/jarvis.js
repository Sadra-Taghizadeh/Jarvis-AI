import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useJarvisStore = defineStore('jarvis', () => {
  const messages = ref([])
  const isConnected = ref(false)
  const isTyping = ref(false)

  function addMessage(message) {
    messages.value.push({
      ...message,
      timestamp: new Date()
    })
  }

  function clearMessages() {
    messages.value = []
  }

  return {
    messages,
    isConnected,
    isTyping,
    addMessage,
    clearMessages
  }
})
