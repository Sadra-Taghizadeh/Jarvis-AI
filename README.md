# Jarvis AI Assistant

A desktop AI assistant that controls your computer using voice and text commands, powered by multiple AI providers.

![Jarvis](https://img.shields.io/badge/Jarvis-AI_Assistant-00d4ff?style=for-the-badge&logo=javascript&logoColor=white)
![Vue](https://img.shields.io/badge/Vue_3-35495E?style=for-the-badge&logo=vuedotjs&logoColor=4FC08D)
![Electron](https://img.shields.io/badge/Electron-47848F?style=for-the-badge&logo=electron&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

## Features

### Core
- **Text Chat** — Natural language commands
- **App Control** — Open/close any application
- **Multi-step Tasks** — Chain multiple actions together
- **File Operations** — Read, write, append files

### Smart
- **Screen Understanding** — AI analyzes your screen with vision models
- **Memory** — Remembers facts across sessions
- **Reminders** — Set and manage reminders
- **Web Search & Read** — Search Google and extract real data from results
- **Background Tasks** — Long tasks run in background with notifications

### Desktop
- **System Tray** — Minimize to tray
- **Global Hotkey** — `Ctrl+Shift+J` to focus
- **Auto-start** — Boot with Windows
- **Window Controls** — Minimize, maximize, close

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Vue 3 + Vite + Pinia |
| Desktop | Electron 30 |
| Backend | Python + WebSockets |
| AI Chat | OpenCode.ai (DeepSeek) |
| Vision | Google AI Studio (Gemini) |
| Computer Control | PyAutoGUI |

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- npm

### Installation

```bash
# Clone the repo
git clone https://github.com/Sadra-Taghizadeh/Jarvis-AI.git
cd Jarvis-AI

# Setup backend
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux
pip install -r requirements.txt

# Setup frontend
cd ../frontend
npm install
```

### Configuration

Copy the example env file and add your API keys:

```bash
cp .env.example .env
```

Edit `.env` with your API keys:

```env
OPENROUTER_API_KEY=your_opencode_api_key
OPENROUTER_BASE_URL=https://opencode.ai/zen/v1
AI_MODEL=deepseek-v4-flash-free
GOOGLE_AI_KEY=your_google_ai_studio_key
GOOGLE_VISION_MODEL=gemini-2.5-flash
```

### Running

**Terminal 1 — Backend:**
```bash
cd backend
venv\Scripts\activate
python main.py
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
```

Open http://localhost:5173

**Or use the start script:**
```bash
start-jarvis.bat
```

## API Keys

| Provider | Purpose | Get Key |
|----------|---------|---------|
| OpenCode.ai | Chat AI | https://opencode.ai |
| Google AI Studio | Vision/Screen | https://aistudio.google.com/apikey |

## Usage Examples

```
"open notepad and write do homework"
"search for Vue.js tutorial on Google"
"take a screenshot and save it to my desktop"
"remember that my birthday is January 15"
"remind me to call mom at 5pm"
"what's on my screen right now?"
"search for Rasht weather, write a date plan"
```

## Project Structure

```
Jarvis-AI/
├── backend/
│   ├── main.py              # WebSocket server
│   ├── ai_brain.py           # AI processing + action mapping
│   ├── computer.py           # Computer control (apps, keyboard, files)
│   ├── screen.py             # Screen vision + search scraping
│   ├── memory.py             # Persistent memory system
│   ├── requirements.txt      # Python dependencies
│   └── memory/               # Stored conversations & facts
├── frontend/
│   ├── src/
│   │   ├── App.vue           # Main UI
│   │   ├── components/
│   │   │   ├── ChatWindow.vue
│   │   │   └── VoiceButton.vue
│   │   └── stores/jarvis.js
│   ├── electron.js           # Electron desktop wrapper
│   ├── vite.config.js
│   └── package.json
├── .env.example
├── start-jarvis.bat
└── README.md
```

## Desktop App

Build the Electron app:

```bash
cd frontend
npm run build
npx electron-packager . "Jarvis AI Assistant" --platform=win32 --arch=x64 --out=release --overwrite
```

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Shift+J` | Focus Jarvis |
| `Ctrl+Shift+Q` | Quit Jarvis |
| `Enter` | Send message |

## License

MIT
