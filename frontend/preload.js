const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('electronAPI', {
  minimize: () => ipcRenderer.invoke('window-minimize'),
  maximize: () => ipcRenderer.invoke('window-maximize'),
  close: () => ipcRenderer.invoke('window-close'),
  getConfig: () => ipcRenderer.invoke('get-config'),
  saveConfig: (config) => ipcRenderer.invoke('save-config', config),
  restartBackend: () => ipcRenderer.invoke('restart-backend'),
  getToken: () => ipcRenderer.invoke('get-token'),
  onFocusInput: (callback) => ipcRenderer.on('focus-input', callback)
})
