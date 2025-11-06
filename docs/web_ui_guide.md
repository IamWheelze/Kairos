# Kairos Web UI Guide

## Overview

The Kairos Web UI provides a modern, browser-based interface for controlling the voice-activated presentation system. Built with FastAPI, WebSockets, and responsive design, it offers real-time updates and an intuitive user experience.

## Features

### 🎤 Voice Control Panel
- **System Control**: Start/Stop the Kairos system
- **Voice Recording**: Record voice commands with adjustable duration (1-10 seconds)
- **File Upload**: Drag-and-drop or browse to upload audio files (.wav, .mp3, .m4a)
- **Visual Feedback**: Real-time voice activity visualization

### 📝 Transcription & Results
- **Real-time Transcription**: See transcribed speech instantly
- **Intent Recognition**: View recognized intents and parameters
- **Command History**: Track all processed commands with timestamps
- **Success Indicators**: Visual feedback for command execution status

### 🖥️ Presentation Control
- **Quick Commands**: One-click buttons for common actions
  - Next Slide
  - Previous Slide
  - Start Presentation
  - Stop Presentation
- **Jump to Slide**: Navigate directly to any slide number
- **Current Slide Display**: Large, easy-to-read current slide indicator
- **Presentation List**: View available presentations

### ⚙️ Settings Panel
- **ASR Engine Selection**: Choose from multiple speech recognition engines
  - Google Speech Recognition (default)
  - CMU Sphinx (offline)
  - OpenAI Whisper
  - Google Cloud Speech
  - Wit.ai
- **Language Settings**: Support for multiple languages
- **Audio Configuration**: Adjust sample rate
- **API Client Settings**: Configure presentation software connection

## Getting Started

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Web UI

1. Start the web server:
```bash
python run_web_ui.py
```

2. Open your browser and navigate to:
```
http://localhost:8000
```

### Command Line Options

```bash
python run_web_ui.py --help
```

Options:
- `--host`: Host to bind to (default: 0.0.0.0)
- `--port`: Port to bind to (default: 8000)
- `--reload`: Enable auto-reload for development

Example:
```bash
python run_web_ui.py --host 127.0.0.1 --port 3000 --reload
```

## Usage Guide

### Starting the System

1. Click the **"Start System"** button in the header
2. Wait for the status badge to change to "Running"
3. The recording button will become enabled

### Voice Commands

#### Recording from Microphone

1. Ensure the system is running
2. Adjust the duration slider (1-10 seconds)
3. Click **"Start Recording"**
4. Speak your command clearly
5. Recording will automatically stop after the set duration
6. View the transcription and intent results

#### Processing Audio Files

1. Ensure the system is running
2. Drag and drop an audio file onto the upload area, or click to browse
3. Click **"Process File"**
4. View the transcription and intent results

### Text Commands

Use the **Quick Commands** buttons for instant control:
- Click any button to execute the corresponding command
- Results appear in the transcription panel

### Jump to Specific Slide

1. Enter the slide number in the input field
2. Click **"Go"**
3. The presentation will jump to that slide

### Viewing Command History

- All processed commands appear in the **Command History** panel
- Each entry shows:
  - Timestamp
  - Command text
  - Intent
  - Success/failure status
- Click the trash icon to clear history

### Configuring Settings

1. Click the **"Settings"** button on the right side of the screen
2. Adjust settings:
   - **ASR Engine**: Choose speech recognition engine
   - **Language**: Select language for recognition
   - **Sample Rate**: Audio quality setting
   - **API Client**: Select presentation software connection type
3. Click **"Save Settings"** to apply changes
4. Click **"Reset to Default"** to restore defaults

## API Endpoints

The web UI communicates with the backend through these REST API endpoints:

### System Control
- `GET /api/system/status` - Get system status
- `POST /api/system/start` - Start the system
- `POST /api/system/stop` - Stop the system

### Voice Processing
- `POST /api/voice/record` - Record and process voice command
  ```json
  {"duration": 5}
  ```
- `POST /api/voice/process-file` - Process uploaded audio file
  - Multipart form data with file

### Text Commands
- `POST /api/command/text` - Process text command
  ```json
  {"command": "next slide"}
  ```

### Presentation Control
- `GET /api/presentation/current-slide` - Get current slide number
- `GET /api/presentation/list` - Get list of presentations

### Settings
- `POST /api/settings/update` - Update configuration
  ```json
  {
    "asrEngine": "google",
    "language": "en-US",
    "sampleRate": 44100,
    "apiClient": "http",
    "apiUrl": "http://127.0.0.1:50001"
  }
  ```

### WebSocket
- `WS /ws` - Real-time updates
  - Status changes
  - Transcription updates
  - System events

## WebSocket Messages

The UI receives real-time updates via WebSocket:

### Status Update
```json
{
  "type": "status_update",
  "status": "running|stopped|recording"
}
```

### Transcription
```json
{
  "type": "transcription",
  "text": "next slide",
  "intent": "next_slide"
}
```

## Customization

### Changing Colors

Edit `/src/kairos/web/static/css/main.css` and modify the CSS variables:

```css
:root {
    --primary-color: #4a90e2;
    --secondary-color: #50c878;
    --danger-color: #e74c3c;
    /* ... etc */
}
```

### Adding Custom Commands

1. Add a button in `/src/kairos/web/templates/index.html`:
```html
<button class="quick-cmd-btn" data-command="your command">
    <i class="fas fa-icon"></i>
    <span>Your Command</span>
</button>
```

2. The command will automatically be processed when clicked

### Modifying Layout

The UI uses CSS Grid for layout. Adjust the grid in `main.css`:

```css
.main-content {
    grid-template-columns: 1fr 1.5fr 1fr;
}
```

## Troubleshooting

### Web UI won't start
- Check that port 8000 is not in use
- Try a different port: `python run_web_ui.py --port 3000`
- Ensure all dependencies are installed

### System status shows "Stopped" but won't start
- Check the browser console for errors (F12)
- Check server logs for error messages
- Ensure Python backend is running properly

### Voice recording not working
- Ensure system is started (click "Start System")
- Check browser permissions for microphone access
- Try processing an audio file first to verify ASR is working

### WebSocket connection failed
- Check that the server is running
- Verify no firewall is blocking WebSocket connections
- Try refreshing the page

### Commands not executing
- Verify the system status is "Running"
- Check that the presentation software API is configured
- Review the intent recognition results

## Browser Compatibility

Tested and supported on:
- ✅ Chrome/Edge (recommended)
- ✅ Firefox
- ✅ Safari
- ⚠️ Internet Explorer (not supported)

## Performance Tips

1. **Recording Duration**: Shorter durations (2-5s) work best for clear commands
2. **Audio Quality**: Use higher sample rates (44.1kHz) for better recognition
3. **Network**: For remote access, use a stable network connection
4. **Browser**: Keep browser updated for best WebSocket performance

## Security Considerations

- The default configuration binds to `0.0.0.0` (all interfaces)
- For production, consider:
  - Using a reverse proxy (nginx, Apache)
  - Adding authentication
  - Using HTTPS
  - Restricting to localhost or specific IPs

Example for localhost only:
```bash
python run_web_ui.py --host 127.0.0.1
```

## Support

For issues or questions:
- Check the main README.md
- Review the FRD documentation in `/docs/frd.md`
- Check the architecture documentation in `/docs/architecture.md`
