// Kairos Voice-Activated Presentation Control - Main JavaScript

class KairosApp {
    constructor() {
        this.systemRunning = false;
        this.recording = false;
        this.selectedFile = null;
        this.commandHistory = [];
        this.websocket = null;

        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadSettings();
        this.checkSystemStatus();
        this.initWebSocket();
    }

    setupEventListeners() {
        // System Control
        document.getElementById('startStopBtn').addEventListener('click', () => this.toggleSystem());

        // Recording Control
        document.getElementById('recordBtn').addEventListener('click', () => this.toggleRecording());
        document.getElementById('durationSlider').addEventListener('input', (e) => {
            document.getElementById('durationValue').textContent = e.target.value;
        });

        // File Upload
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('audioFileInput');

        uploadArea.addEventListener('click', () => fileInput.click());
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('drag-over');
        });
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('drag-over');
        });
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('drag-over');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.handleFileSelect(files[0]);
            }
        });
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.handleFileSelect(e.target.files[0]);
            }
        });

        document.getElementById('processFileBtn').addEventListener('click', () => this.processAudioFile());

        // Quick Commands
        document.querySelectorAll('.quick-cmd-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const command = btn.dataset.command;
                this.processTextCommand(command);
            });
        });

        // Jump to Slide
        document.getElementById('jumpSlideBtn').addEventListener('click', () => {
            const slideNum = document.getElementById('slideNumber').value;
            if (slideNum) {
                this.processTextCommand(`go to slide ${slideNum}`);
            }
        });

        // Refresh Buttons
        document.getElementById('refreshSlideBtn').addEventListener('click', () => this.getCurrentSlide());
        document.getElementById('refreshPresentationsBtn').addEventListener('click', () => this.getPresentations());

        // History
        document.getElementById('clearHistoryBtn').addEventListener('click', () => this.clearHistory());

        // Settings
        document.getElementById('settingsToggle').addEventListener('click', () => this.toggleSettings());
        document.getElementById('saveSettingsBtn').addEventListener('click', () => this.saveSettings());
        document.getElementById('resetSettingsBtn').addEventListener('click', () => this.resetSettings());
        document.getElementById('apiClient').addEventListener('change', (e) => {
            const httpUrlGroup = document.getElementById('httpUrlGroup');
            httpUrlGroup.style.display = e.target.value === 'http' ? 'block' : 'none';
        });

        // NLP Provider Settings
        document.getElementById('nlpProvider').addEventListener('change', (e) => {
            this.handleNLPProviderChange(e.target.value);
        });

        // Bible Controls
        document.getElementById('showVerseBtn').addEventListener('click', () => this.showBibleVerse());
        document.getElementById('bibleReference').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.showBibleVerse();
        });
        document.getElementById('bibleTranslation').addEventListener('change', (e) => {
            this.setBibleTranslation(e.target.value);
        });
        document.getElementById('nextVerseBtn').addEventListener('click', () => this.nextBibleVerse());
        document.getElementById('prevVerseBtn').addEventListener('click', () => this.previousBibleVerse());
    }

    // WebSocket Connection
    initWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;

        try {
            this.websocket = new WebSocket(wsUrl);

            this.websocket.onopen = () => {
                console.log('WebSocket connected');
            };

            this.websocket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleWebSocketMessage(data);
            };

            this.websocket.onerror = (error) => {
                console.error('WebSocket error:', error);
            };

            this.websocket.onclose = () => {
                console.log('WebSocket disconnected');
                // Attempt to reconnect after 5 seconds
                setTimeout(() => this.initWebSocket(), 5000);
            };
        } catch (error) {
            console.error('WebSocket initialization error:', error);
        }
    }

    handleWebSocketMessage(data) {
        if (data.type === 'status_update') {
            this.updateSystemStatus(data.status);
        } else if (data.type === 'transcription') {
            this.updateTranscription(data);
        }
    }

    // System Control
    async toggleSystem() {
        const btn = document.getElementById('startStopBtn');
        const icon = btn.querySelector('i');
        const text = btn.querySelector('span');

        this.showLoading(true);

        try {
            if (this.systemRunning) {
                await this.apiCall('/api/system/stop', 'POST');
                this.systemRunning = false;
                text.textContent = 'Start System';
                icon.className = 'fas fa-power-off';
                document.getElementById('recordBtn').disabled = true;
                this.showToast('System stopped', 'warning');
            } else {
                await this.apiCall('/api/system/start', 'POST');
                this.systemRunning = true;
                text.textContent = 'Stop System';
                icon.className = 'fas fa-power-off';
                document.getElementById('recordBtn').disabled = false;
                this.showToast('System started successfully', 'success');
            }

            this.updateSystemStatus(this.systemRunning ? 'running' : 'stopped');
        } catch (error) {
            this.showToast('Failed to toggle system: ' + error.message, 'error');
        } finally {
            this.showLoading(false);
        }
    }

    async checkSystemStatus() {
        try {
            const response = await this.apiCall('/api/system/status');
            this.systemRunning = response.status === 'running';
            this.updateSystemStatus(response.status);

            const btn = document.getElementById('startStopBtn');
            const text = btn.querySelector('span');
            text.textContent = this.systemRunning ? 'Stop System' : 'Start System';
            document.getElementById('recordBtn').disabled = !this.systemRunning;
        } catch (error) {
            console.error('Failed to check system status:', error);
        }
    }

    updateSystemStatus(status) {
        const statusBadge = document.getElementById('systemStatus');
        statusBadge.className = 'status-badge';

        if (status === 'running') {
            statusBadge.classList.add('status-running');
            statusBadge.textContent = 'Running';
        } else if (status === 'recording') {
            statusBadge.classList.add('status-recording');
            statusBadge.textContent = 'Recording';
        } else {
            statusBadge.classList.add('status-stopped');
            statusBadge.textContent = 'Stopped';
        }
    }

    // Recording Control
    async toggleRecording() {
        const btn = document.getElementById('recordBtn');
        const icon = btn.querySelector('i');
        const text = btn.querySelector('span');
        const visualizer = document.getElementById('voiceVisualizer').parentElement;

        if (this.recording) {
            // Stop recording
            this.recording = false;
            btn.classList.remove('recording');
            text.textContent = 'Start Recording';
            icon.className = 'fas fa-microphone';
            visualizer.classList.remove('active');
            this.updateSystemStatus('running');
        } else {
            // Start recording
            this.recording = true;
            btn.classList.add('recording');
            text.textContent = 'Recording...';
            icon.className = 'fas fa-stop';
            visualizer.classList.add('active');
            this.updateSystemStatus('recording');

            const duration = parseInt(document.getElementById('durationSlider').value);

            try {
                this.showLoading(true);
                const response = await this.apiCall('/api/voice/record', 'POST', { duration });

                this.recording = false;
                btn.classList.remove('recording');
                text.textContent = 'Start Recording';
                icon.className = 'fas fa-microphone';
                visualizer.classList.remove('active');
                this.updateSystemStatus('running');

                if (response.ok) {
                    this.displayResult(response);
                    this.showToast('Voice command processed', 'success');
                } else {
                    this.showToast('Recording failed: ' + (response.error || 'Unknown error'), 'error');
                }
            } catch (error) {
                this.recording = false;
                btn.classList.remove('recording');
                visualizer.classList.remove('active');
                this.showToast('Recording error: ' + error.message, 'error');
            } finally {
                this.showLoading(false);
            }
        }
    }

    // File Processing
    handleFileSelect(file) {
        this.selectedFile = file;
        const uploadArea = document.getElementById('uploadArea');
        uploadArea.querySelector('p').textContent = `Selected: ${file.name}`;
        uploadArea.querySelector('i').className = 'fas fa-file-audio';
        document.getElementById('processFileBtn').disabled = false;
    }

    async processAudioFile() {
        if (!this.selectedFile) {
            this.showToast('No file selected', 'warning');
            return;
        }

        const formData = new FormData();
        formData.append('file', this.selectedFile);

        this.showLoading(true);

        try {
            const response = await fetch('/api/voice/process-file', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (result.ok) {
                this.displayResult(result);
                this.showToast('Audio file processed successfully', 'success');
            } else {
                this.showToast('Processing failed: ' + (result.error || 'Unknown error'), 'error');
            }
        } catch (error) {
            this.showToast('Error processing file: ' + error.message, 'error');
        } finally {
            this.showLoading(false);
        }
    }

    // Text Command Processing
    async processTextCommand(command) {
        this.showLoading(true);

        try {
            const response = await this.apiCall('/api/command/text', 'POST', { command });

            if (response.ok || response.command) {
                this.displayResult({
                    ok: true,
                    transcription: command,
                    intent: response.command || 'unknown',
                    params: {},
                    result: response
                });
                this.showToast('Command executed', 'success');
            } else {
                this.showToast('Command failed: ' + (response.error || 'Unknown error'), 'error');
            }
        } catch (error) {
            this.showToast('Error: ' + error.message, 'error');
        } finally {
            this.showLoading(false);
        }
    }

    // Display Results
    displayResult(result) {
        // Update transcription
        if (result.transcription) {
            const transcriptionEl = document.getElementById('transcriptionText');
            transcriptionEl.innerHTML = `"${result.transcription}"`;
        }

        // Update intent
        document.getElementById('intentName').textContent = result.intent || '-';
        document.getElementById('intentParams').textContent =
            result.params && Object.keys(result.params).length > 0
                ? JSON.stringify(result.params)
                : '-';
        document.getElementById('intentStatus').textContent = result.ok ? '✓ Success' : '✗ Failed';
        document.getElementById('intentStatus').style.color = result.ok ? 'var(--success-color)' : 'var(--danger-color)';

        // Add to history
        this.addToHistory({
            time: new Date(),
            command: result.transcription || result.intent,
            intent: result.intent,
            success: result.ok
        });
    }

    updateTranscription(data) {
        const transcriptionEl = document.getElementById('transcriptionText');
        transcriptionEl.innerHTML = `"${data.text}"`;

        if (data.intent) {
            document.getElementById('intentName').textContent = data.intent;
        }
    }

    // Command History
    addToHistory(item) {
        this.commandHistory.unshift(item);
        this.renderHistory();
    }

    renderHistory() {
        const container = document.getElementById('commandHistory');

        if (this.commandHistory.length === 0) {
            container.innerHTML = '<p class="placeholder">No commands processed yet.</p>';
            return;
        }

        container.innerHTML = this.commandHistory.map(item => `
            <div class="history-item ${item.success ? '' : 'error'}">
                <div class="history-item-header">
                    <span class="history-item-time">${this.formatTime(item.time)}</span>
                    <span>${item.success ? '✓' : '✗'}</span>
                </div>
                <div class="history-item-command">${item.command}</div>
                <div style="font-size: 0.85rem; color: var(--text-secondary); margin-top: 0.25rem;">
                    Intent: ${item.intent || 'unknown'}
                </div>
            </div>
        `).join('');
    }

    clearHistory() {
        this.commandHistory = [];
        this.renderHistory();
        this.showToast('History cleared', 'success');
    }

    // Presentation Control
    async getCurrentSlide() {
        try {
            const response = await this.apiCall('/api/presentation/current-slide');
            if (response.ok && response.slide) {
                document.getElementById('currentSlideNumber').textContent = response.slide;
            }
        } catch (error) {
            console.error('Failed to get current slide:', error);
        }
    }

    async getPresentations() {
        try {
            const response = await this.apiCall('/api/presentation/list');
            this.renderPresentations(response.presentations || []);
        } catch (error) {
            console.error('Failed to get presentations:', error);
        }
    }

    renderPresentations(presentations) {
        const container = document.getElementById('presentationsList');

        if (presentations.length === 0) {
            container.innerHTML = '<p class="placeholder">No presentations loaded.</p>';
            return;
        }

        container.innerHTML = presentations.map(pres => `
            <div class="presentation-item">
                <i class="fas fa-file-powerpoint"></i>
                ${pres.name || pres.id}
            </div>
        `).join('');
    }

    // Settings
    toggleSettings() {
        const drawer = document.getElementById('settingsDrawer');
        drawer.classList.toggle('open');
    }

    loadSettings() {
        const settings = JSON.parse(localStorage.getItem('kairosSettings') || '{}');

        if (settings.asrEngine) document.getElementById('asrEngine').value = settings.asrEngine;
        if (settings.language) document.getElementById('language').value = settings.language;
        if (settings.sampleRate) document.getElementById('sampleRate').value = settings.sampleRate;
        if (settings.apiClient) document.getElementById('apiClient').value = settings.apiClient;
        if (settings.apiUrl) document.getElementById('apiUrl').value = settings.apiUrl;
        if (settings.nlpProvider) document.getElementById('nlpProvider').value = settings.nlpProvider;
        if (settings.openaiKey) document.getElementById('openaiKey').value = settings.openaiKey;
        if (settings.ollamaUrl) document.getElementById('ollamaUrl').value = settings.ollamaUrl;

        // Trigger change events
        document.getElementById('apiClient').dispatchEvent(new Event('change'));
        if (settings.nlpProvider) {
            this.handleNLPProviderChange(settings.nlpProvider);
        }

        // Load available providers
        this.loadNLPProviders();
    }

    async saveSettings() {
        const settings = {
            asrEngine: document.getElementById('asrEngine').value,
            language: document.getElementById('language').value,
            sampleRate: document.getElementById('sampleRate').value,
            apiClient: document.getElementById('apiClient').value,
            apiUrl: document.getElementById('apiUrl').value,
            nlpProvider: document.getElementById('nlpProvider').value,
            openaiKey: document.getElementById('openaiKey').value,
            ollamaUrl: document.getElementById('ollamaUrl').value
        };

        localStorage.setItem('kairosSettings', JSON.stringify(settings));

        try {
            await this.apiCall('/api/settings/update', 'POST', settings);

            // Switch NLP provider if system is running
            if (this.systemRunning) {
                await this.selectNLPProvider(settings.nlpProvider);
            }

            this.showToast('Settings saved successfully', 'success');
        } catch (error) {
            this.showToast('Failed to save settings: ' + error.message, 'error');
        }
    }

    resetSettings() {
        localStorage.removeItem('kairosSettings');
        document.getElementById('asrEngine').value = 'google';
        document.getElementById('language').value = 'en-US';
        document.getElementById('sampleRate').value = '44100';
        document.getElementById('apiClient').value = 'stub';
        document.getElementById('apiUrl').value = '';
        document.getElementById('nlpProvider').value = 'rule-based';
        document.getElementById('openaiKey').value = '';
        document.getElementById('ollamaUrl').value = 'http://localhost:11434';
        this.handleNLPProviderChange('rule-based');
        this.showToast('Settings reset to default', 'success');
    }

    // NLP Provider Management
    handleNLPProviderChange(providerId) {
        const openaiKeyGroup = document.getElementById('openaiKeyGroup');
        const ollamaUrlGroup = document.getElementById('ollamaUrlGroup');

        // Show/hide relevant config fields
        if (providerId.startsWith('openai-')) {
            openaiKeyGroup.style.display = 'block';
            ollamaUrlGroup.style.display = 'none';
        } else if (providerId.startsWith('ollama-')) {
            openaiKeyGroup.style.display = 'none';
            ollamaUrlGroup.style.display = 'block';
        } else {
            openaiKeyGroup.style.display = 'none';
            ollamaUrlGroup.style.display = 'none';
        }
    }

    async loadNLPProviders() {
        try {
            const data = await this.apiCall('/api/nlp/providers');

            if (data.ok && data.current) {
                this.updateProviderInfo(data.current);
            }
        } catch (error) {
            console.error('Failed to load NLP providers:', error);
        }
    }

    async selectNLPProvider(providerId) {
        try {
            const config = {};

            // Add provider-specific config
            if (providerId.startsWith('openai-')) {
                const apiKey = document.getElementById('openaiKey').value;
                if (apiKey) {
                    config.api_key = apiKey;
                }
            } else if (providerId.startsWith('ollama-')) {
                const baseUrl = document.getElementById('ollamaUrl').value;
                if (baseUrl) {
                    config.base_url = baseUrl;
                }
            }

            const data = await this.apiCall('/api/nlp/provider/select', 'POST', {
                provider_id: providerId,
                config: config
            });

            if (data.ok) {
                this.updateProviderInfo(data.provider);
                this.showToast(data.message, 'success');
            } else {
                this.showToast(data.error, 'error');
            }
        } catch (error) {
            this.showToast('Failed to switch provider: ' + error.message, 'error');
        }
    }

    updateProviderInfo(providerInfo) {
        const providerInfoDiv = document.getElementById('providerInfo');
        const currentProvider = document.getElementById('currentProvider');
        const providerCost = document.getElementById('providerCost');

        currentProvider.textContent = providerInfo.name;

        if (providerInfo.cost_per_request === 0) {
            providerCost.textContent = 'FREE';
        } else {
            providerCost.textContent = `$${providerInfo.cost_per_request.toFixed(4)}`;
        }

        providerInfoDiv.style.display = 'block';
    }

    // API Calls
    async apiCall(endpoint, method = 'GET', data = null) {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json'
            }
        };

        if (data && method !== 'GET') {
            options.body = JSON.stringify(data);
        }

        const response = await fetch(endpoint, options);

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        return await response.json();
    }

    // UI Utilities
    showToast(message, type = 'success') {
        const container = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;

        const icon = type === 'success' ? 'check-circle' :
                     type === 'error' ? 'exclamation-circle' :
                     'exclamation-triangle';

        toast.innerHTML = `
            <div class="toast-header">
                <i class="fas fa-${icon}"></i>
                <span>${type.charAt(0).toUpperCase() + type.slice(1)}</span>
            </div>
            <div>${message}</div>
        `;

        container.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    showLoading(show) {
        document.getElementById('loadingOverlay').style.display = show ? 'flex' : 'none';
    }

    // Bible Methods
    async showBibleVerse() {
        const reference = document.getElementById('bibleReference').value.trim();

        if (!reference) {
            this.showToast('Please enter a Bible reference (e.g., John 3:16)', 'warning');
            return;
        }

        try {
            const data = await this.apiCall('/api/bible/verse', 'POST', {
                reference: reference,
                translation: document.getElementById('bibleTranslation').value
            });

            if (data.ok) {
                this.displayBibleVerse(data);
                this.showToast('Bible verse loaded', 'success');
            } else {
                this.showToast(data.error || 'Failed to load verse', 'error');
            }
        } catch (error) {
            this.showToast('Error loading Bible verse: ' + error.message, 'error');
        }
    }

    async setBibleTranslation(translation) {
        try {
            const data = await this.apiCall('/api/bible/translation', 'POST', {
                translation: translation
            });

            if (data.ok) {
                this.showToast(`Translation changed to ${translation}`, 'success');
            }
        } catch (error) {
            this.showToast('Error changing translation: ' + error.message, 'error');
        }
    }

    async nextBibleVerse() {
        try {
            const data = await this.apiCall('/api/bible/next', 'POST');

            if (data.ok) {
                this.displayBibleVerse(data);
                this.showToast('Next verse loaded', 'success');
            } else {
                this.showToast(data.error || 'No next verse available', 'warning');
            }
        } catch (error) {
            this.showToast('Error loading next verse: ' + error.message, 'error');
        }
    }

    async previousBibleVerse() {
        try {
            const data = await this.apiCall('/api/bible/previous', 'POST');

            if (data.ok) {
                this.displayBibleVerse(data);
                this.showToast('Previous verse loaded', 'success');
            } else {
                this.showToast(data.error || 'No previous verse available', 'warning');
            }
        } catch (error) {
            this.showToast('Error loading previous verse: ' + error.message, 'error');
        }
    }

    displayBibleVerse(data) {
        const display = document.getElementById('bibleVerseDisplay');
        const reference = document.getElementById('bibleVerseReference');
        const text = document.getElementById('bibleVerseText');

        reference.textContent = `${data.reference} (${data.translation})`;
        text.textContent = data.text;

        display.style.display = 'block';

        // Update the reference input to current verse
        document.getElementById('bibleReference').value = data.reference;
    }

    formatTime(date) {
        return date.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.kairosApp = new KairosApp();
});
