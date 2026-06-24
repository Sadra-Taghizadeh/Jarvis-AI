const { app, BrowserWindow, Tray, Menu, globalShortcut, nativeImage, ipcMain } = require('electron')
const path = require('path')
const fs = require('fs')

let mainWindow
let tray
let isQuitting = false
let backendPid = null

const CONFIG_PATH = path.join(app.getPath('userData'), 'config.json')
const PROJECT_ROOT = path.join(__dirname, '..', '..', '..')
const PID_PATH = path.join(PROJECT_ROOT, 'backend', 'backend.pid')

function loadConfig() {
  try {
    if (fs.existsSync(CONFIG_PATH)) {
      return JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'))
    }
  } catch (e) {}
  return { autoStart: false, minimizeToTray: true }
}

function saveConfig(config) {
  fs.writeFileSync(CONFIG_PATH, JSON.stringify(config, null, 2))
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 950,
    height: 750,
    minWidth: 600,
    minHeight: 400,
    frame: false,
    titleBarStyle: 'hidden',
    backgroundColor: '#0a0a0f',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
    icon: getIconPath(),
    show: false
  })

  const distPath = path.join(__dirname, 'dist', 'index.html')
  const isDev = !fs.existsSync(distPath)

  console.log('isDev:', isDev, 'distPath:', distPath)

  if (isDev) {
    mainWindow.loadURL('http://localhost:5173')
  } else {
    mainWindow.loadURL(`file:///${distPath.replace(/\\/g, '/')}`)
  }

  mainWindow.once('ready-to-show', () => {
    mainWindow.show()
  })

  mainWindow.on('close', (e) => {
    const config = loadConfig()
    if (!isQuitting && config.minimizeToTray) {
      e.preventDefault()
      mainWindow.hide()
      return false
    }
  })

  mainWindow.on('closed', () => {
    mainWindow = null
  })

  createTray()
}

function getIconPath() {
  const iconPath = path.join(__dirname, 'src/assets/icon.png')
  if (fs.existsSync(iconPath)) return iconPath

  const fallback = path.join(__dirname, 'icon.ico')
  if (fs.existsSync(fallback)) return fallback

  return nativeImage.createEmpty()
}

function createTray() {
  tray = new Tray(getIconPath())

  const config = loadConfig()

  const contextMenu = Menu.buildFromTemplate([
    { label: 'Show Jarvis', click: () => mainWindow && mainWindow.show() },
    { type: 'separator' },
    {
      label: 'Minimize to Tray',
      type: 'checkbox',
      checked: config.minimizeToTray,
      click: (menuItem) => {
        config.minimizeToTray = menuItem.checked
        saveConfig(config)
      }
    },
    {
      label: 'Start on Boot',
      type: 'checkbox',
      checked: config.autoStart,
      click: (menuItem) => {
        config.autoStart = menuItem.checked
        app.setLoginItemSettings({ openAtLogin: menuItem.checked })
        saveConfig(config)
      }
    },
    { type: 'separator' },
    { label: 'Restart Backend', click: () => restartBackend() },
    { type: 'separator' },
    { label: 'Quit Jarvis', click: () => { isQuitting = true; app.quit() } }
  ])

  tray.setToolTip('Jarvis AI Assistant - Ctrl+Shift+J to focus')
  tray.setContextMenu(contextMenu)

  tray.on('click', () => {
    if (mainWindow) {
      mainWindow.show()
      mainWindow.focus()
    }
  })
}

function restartBackend() {
  const { exec } = require('child_process')
  const backendPath = path.join(PROJECT_ROOT, 'backend')

  if (backendPid) {
    try {
      process.kill(backendPid)
    } catch (e) {}
    backendPid = null
  }

  try {
    if (fs.existsSync(PID_PATH)) {
      const pid = parseInt(fs.readFileSync(PID_PATH, 'utf8').trim(), 10)
      if (!isNaN(pid)) {
        try { process.kill(pid) } catch (e) {}
      }
      fs.unlinkSync(PID_PATH)
    }
  } catch (e) {}

  setTimeout(() => {
    exec('cd /d "' + backendPath + '" && venv\\Scripts\\activate && start python main.py', (err) => {
      if (err) console.error('Backend restart error:', err)
      else console.log('Backend restarted')
    })
  }, 1000)
}

app.whenReady().then(() => {
  createWindow()

  globalShortcut.register('CommandOrControl+Shift+J', () => {
    if (mainWindow) {
      if (mainWindow.isVisible()) {
        mainWindow.focus()
      } else {
        mainWindow.show()
        mainWindow.focus()
      }
      mainWindow.webContents.send('focus-input')
    }
  })

  globalShortcut.register('CommandOrControl+Shift+Q', () => {
    isQuitting = true
    app.quit()
  })
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow()
  } else {
    mainWindow.show()
  }
})

app.on('will-quit', () => {
  globalShortcut.unregisterAll()
})

ipcMain.handle('window-minimize', () => mainWindow && mainWindow.minimize())
ipcMain.handle('window-maximize', () => {
  if (mainWindow) {
    mainWindow.isMaximized() ? mainWindow.unmaximize() : mainWindow.maximize()
  }
})
ipcMain.handle('window-close', () => mainWindow && mainWindow.hide())
ipcMain.handle('get-config', () => loadConfig())
ipcMain.handle('save-config', (event, config) => saveConfig(config))
ipcMain.handle('restart-backend', () => restartBackend())
ipcMain.handle('get-token', () => {
  const possiblePaths = [
    path.join(__dirname, '..', '..', '..', 'backend', '.ws_token'),
    path.join(__dirname, '..', 'backend', '.ws_token'),
    path.join(process.cwd(), '..', 'backend', '.ws_token')
  ]
  for (const tokenPath of possiblePaths) {
    try {
      if (fs.existsSync(tokenPath)) {
        const token = fs.readFileSync(tokenPath, 'utf8').trim()
        console.log('[TOKEN] Read from:', tokenPath)
        return token
      }
    } catch (e) {}
  }
  console.error('[TOKEN] No .ws_token file found in any of:', possiblePaths)
  return null
})
