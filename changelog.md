# Changelog

Tutte le modifiche rilevanti al progetto BioPosture sono documentate in questo file.

Il formato è basato su [Keep a Changelog](https://keepachangelog.com/it/1.0.0/),
e il progetto aderisce al [Semantic Versioning](https://semver.org/lang/it/).

---

## [2.0.0] - 2024-12-23

### 🌍 Added - Nuove Funzionalità

#### Multi-Platform Support
- **Supporto completo Windows, macOS, Linux**
  - Build nativi per ogni piattaforma
  - Installer professionali (.exe, .dmg, .deb, .AppImage)
  - Backend camera adattivo (CAP_DSHOW su Windows, CAP_ANY su Unix)
  - Font cross-platform (Segoe UI / SF Pro / Ubuntu)

#### Sistema Notifiche Native
- **Windows 10/11**: Toast Notifications tramite `winotify`
- **macOS**: Notification Center tramite `osascript`
- **Linux**: Desktop Notifications tramite `notify-send`
- Cooldown configurabile tra notifiche (default: 8 secondi)
- Tempo ritardo allarme per evitare false positive (default: 5 secondi)

#### Autostart Cross-Platform
- **Windows**: Gestione tramite registro `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`
- **macOS**: LaunchAgents in `~/Library/LaunchAgents/`
- **Linux**: Desktop files in `~/.config/autostart/`
- Supporto flag `--minimized` per avvio in system tray
- Toggle UI per abilitare/disabilitare autostart

#### Interfaccia Utente
- **Material Design** con palette professionale glass morphism
- **Dark/Light Mode** con toggle dinamico senza restart
- **System Tray Integration** con menu contestuale completo
- **Grafico Real-Time** con 60 sample buffer (andamento testa/collo)
- **Barra Efficienza** con percentuale tempo postura corretta
- **Slider Soglia Tolleranza** configurabile 0-100%
- Video feed ottimizzato 768px con overlay landmark anatomici

#### Monitoraggio Avanzato
- **Calibrazione Personalizzata** (5 secondi) per baseline individuale
- **4 Parametri Posturali**:
  - Inclinazione Testa (Head Tilt)
  - Asimmetria Spalle (Shoulder Tilt)
  - Distanza Schermo (basata su distanza interpupillare)
  - Tensione Cervicale (Neck Compression ratio)
- **Data Smoothing** con Exponential Moving Average (α=0.7-0.8)
- **Ricalibrazione On-Demand** in qualsiasi momento

#### Persistenza Dati
- **Configurazione JSON** salvata automaticamente
- Percorsi cross-platform:
  - Windows: `%APPDATA%\BioPosture\config.json`
  - macOS: `~/Library/Application Support/BioPosture/config.json`
  - Linux: `~/.config/BioPosture/config.json`
- **Export KPI** in formato CSV (timestamp, frame totali, efficienza)
- Salvataggio automatico parametri calibrazione

#### Funzionalità Produttività
- **Pausa Monitoraggio** senza chiudere applicazione
- **Stop/Avvia Camera** on-demand
- **Menu System Tray** con accesso rapido a tutte le funzioni
- **Minimizzazione in Tray** per monitoraggio background
- **Cambio Camera** runtime (supporto multi-webcam)

### 🔧 Changed - Modifiche

#### Performance
- **Lazy Loading** modelli MediaPipe (ridotto startup time ~2 secondi)
- **Ottimizzazione Rendering** video con buffer pool
- **Riduzione CPU Usage** ~15% tramite frame skipping intelligente
- **Memory Management** migliorato per sessioni prolungate (8+ ore)

#### Architettura
- **Refactoring Completo** codebase per supporto multi-OS
- **Modularizzazione**: `config_manager.py`, `autostart_manager.py`
- **Separazione Build Scripts** per Windows, macOS, Linux
- **Type Hints** aggiunti per funzioni pubbliche
- **Error Handling** robusto per edge cases

#### UI/UX
- **Interfaccia Ridisegnata** da zero con CustomTkinter 5.2+
- **Palette Colori** aggiornata a Material Design
- **Layout Responsive** adattivo a diverse risoluzioni
- **Icone Tray** colorate dinamicamente (verde=OK, rosso=Alert, arancione=Pausa)
- **Feedback Visivo** migliorato per ogni azione utente

### 🐛 Fixed - Bug Risolti

#### Stabilità
- **Crash su macOS** quando camera viene disconnessa durante runtime
- **Memory Leak** su sessioni >4 ore (leak in buffer grafici)
- **Race Condition** tra thread UI e processing camera
- **Deadlock** occasionale su chiusura applicazione

#### Cross-Platform Issues
- **System Tray** non appariva su alcuni desktop environment Linux (Wayland)
- **Notifiche** non funzionavano su macOS Ventura senza permessi espliciti
- **Autostart** falliva su Linux con path contenenti spazi
- **Camera Backend** non gestito correttamente su non-Windows

#### UI Bugs
- **Grafico** non si aggiornava correttamente dopo resize finestra
- **Slider Tolleranza** non salvava valore su chiusura app
- **Theme Toggle** causava flash visivo
- **Video Feed** aspect ratio distorto su webcam non 16:9

### 🔐 Technical - Dettagli Tecnici

#### Dependencies
- CustomTkinter 5.2.0+ (UI framework moderno)
- MediaPipe 0.10.0+ (pose estimation)
- OpenCV 4.8.0+ (computer vision)
- NumPy 1.24.0+ (calcoli numerici)
- Pillow 10.0.0+ (image processing)
- Pystray 0.19.0+ (system tray)
- PyInstaller 6.0.0+ (packaging)
- winotify 1.1.0 (Windows notifications, opzionale)

#### Build System
- **Windows**: PyInstaller + NSIS (installer ~150MB)
- **macOS**: PyInstaller → .app bundle + create-dmg (DMG ~180MB)
- **Linux**: PyInstaller → binario + dpkg/AppImage (binary ~160MB)
- **High DPI Support**: Awareness configurato per display Retina/4K

#### Algorithms
- **Angle Calculation**: `arctan2` per angoli inclinazione
- **Distance Estimation**: Ratio interpupillary distance / baseline
- **Smoothing**: Exponential Moving Average con alpha adattivo
- **Threshold Scaling**: Dinamico basato su severity factor 0-1

---

## [Unreleased] - Roadmap Futura

### Pianificato per v2.1
- [ ] **Machine Learning**: Classificatore CNN per pattern posturali
- [ ] **Multi-Monitor**: Tracking su quali monitor si lavora
- [ ] **Analytics Dashboard**: Statistiche settimanali/mensili con grafici
- [ ] **Export PDF**: Report posturale professionale
- [ ] **Reminder Stretching**: Suggerimenti esercizi personalizzati

### Pianificato per v3.0
- [ ] **Cloud Sync**: Sincronizzazione dati tra dispositivi
- [ ] **Mobile App**: Companion app iOS/Android
- [ ] **Team Features**: Dashboard aziendali per HR
- [ ] **Gamification**: Punti, achievement, leaderboard
- [ ] **Integrations**: Slack bot, Google Calendar, Fitbit

---

## [1.0.0] - 2025-12-04 

### Initial Release
- Versione Windows-only proof-of-concept
- Monitoraggio base parametri posturali
- Interfaccia Tkinter semplice
- Notifiche Windows basilari

---

## Semantic Versioning

Questo progetto usa [Semantic Versioning](https://semver.org/lang/it/):

- **MAJOR** (X.0.0): Breaking changes, incompatibilità con versioni precedenti
- **MINOR** (x.Y.0): Nuove funzionalità backward-compatible
- **PATCH** (x.y.Z): Bug fixes backward-compatible

---

## Link Utili

- [Repository GitHub](https://github.com/antdf87/BioPosture)
- [Releases](https://github.com/antdf87/BioPosture/releases)
- [Issues](https://github.com/antdf87/BioPosture/issues)
- [Discussions](https://github.com/antdf87/BioPosture/discussions)

---

*Ultimo aggiornamento: 23 Dicembre 2024*
