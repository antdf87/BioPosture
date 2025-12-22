BioPosture: Markerless Kinematic Analysis System

Engineering Release: v2.0.0 (Multi-OS Support)
Author: AntDF87
Domain: Biomedical Engineering / Ergonomics / Computer Vision
License: MIT License



📋 Abstract

BioPosture è una piattaforma software cross-platform progettata per l'analisi cinematica in tempo reale e il monitoraggio ergonomico del rachide cervicale. Sfruttando algoritmi di Computer Vision e reti neurali per la stima della posa (MediaPipe Framework), il sistema trasforma una comune webcam in un sensore biometrico di precisione.

L'obiettivo primario è la prevenzione dei disturbi muscolo-scheletrici (DMS) correlati all'uso prolungato di VDT (Videoterminali), fornendo biofeedback visivo immediato per correggere deviazioni posturali patomeccaniche (es. Text Neck Syndrome).



⚙️ Architettura del Sistema

Il software è sviluppato in Python (v3.10+) e implementa una pipeline di elaborazione a bassa latenza (<30ms):

Acquisizione (Input Layer): Interfacciamento hardware ottimizzato con dispositivi di acquisizione ottica (OpenCV).

Inference (Processing Layer): Estrazione topologica dei landmark facciali (Face Mesh) e corporei (Pose Topology) tramite CNN.

Analisi Geometrica (Logic Layer): Calcolo vettoriale in tempo reale degli angoli di Eulero e stima della profondità basata sulla dimensione iridea.

HMI (Presentation Layer): Interfaccia grafica High-DPI basata su customtkinter con rendering vettoriale e feedback adattivo.



🚀 Funzionalità 

Real-Time Pose Estimation: Monitoraggio continuo di Cervical Tilt (inclinazione testa-collo) e Scapular Symmetry (simmetria spalle).

Screen Distance Estimation: Stima della prossimità relativa senza sensori di profondità (ToF/LiDAR), basata su calibrazione biometrica dell'iride.

Adaptive Notification System: Algoritmo intelligente di cooldown per prevenire la "notification fatigue" (assuefazione agli allarmi).

Background Process: Esecuzione ottimizzata in System Tray (Daemon) per minimizzare l'impatto sulla CPU durante il workflow.

Data Logging: Esportazione delle metriche temporali (KPI) in formato CSV per post-processing statistico (es. MATLAB/Excel).



🛠 Deployment & Installazione

Opzione A: Eseguibile Standalone (Consigliata per End-User)

Questa distribuzione include un ambiente runtime Python isolato. Non è richiesta l'installazione di librerie esterne.

Scaricare l'ultima release dalla sezione Releases.

Eseguire l'installer specifico per il proprio OS:

Windows: BioPosture_Setup_v2.0.exe

macOS: BioPosture_v2.0.dmg (Supporto Apple Silicon/Intel)

Linux: BioPosture_v2.0.tar.gz

Al primo avvio, seguire la procedura guidata di Calibrazione Biometrica (durata: 5s).

Opzione B: Esecuzione da Codice Sorgente (Dev)

Per sviluppatori e ricercatori che desiderano modificare il codice sorgente.

Requisiti: Python 3.10+, pip, virtualenv (consigliato).

# 1. Clona la repository
git clone [https://github.com/antdf87/BioPosture.git](https://github.com/antdf87/BioPosture.git)
cd BioPosture

# 2. Crea ambiente virtuale (opzionale ma raccomandato)
python -m venv venv
source venv/bin/activate  # Su Windows: venv\Scripts\activate

# 3. Installa dipendenze
pip install -r requirements.txt

# 4. Avvia l'applicazione
python bioposture_interface.py


💻 Requisiti di Sistema

Componente

Requisiti Minimi

Requisiti Raccomandati

OS

Windows 10/11, macOS 11+, Linux

Windows 11, macOS 13+

CPU

Dual Core 2.0GHz (x64)

Quad Core i5/M1 o superiore

RAM

4 GB

8 GB

Input

Webcam USB/Integrata (720p)

Webcam HD (1080p) con autofocus

Runtime: Architettura 64-bit, 4GB RAM.

📚 Citazione

Se utilizzi questo software per scopi accademici o di ricerca, per favore cita il progetto utilizzando il file CITATION.cff incluso o il seguente formato BibTeX:

@software{BioPosture2025,
  author = {AntDF87},
  title = {BioPosture: Markerless Kinematic Analysis System},
  year = {2025},
  version = {2.0.0},
  url = {[https://github.com/antdf87/BioPosture](https://github.com/antdf87/BioPosture)}


## 📸 Screenshots

<div align="center">

### Interfaccia Principale
![Interfaccia](docs/screenshots/main_interface.png)

### Processo di Calibrazione
![Calibrazione](docs/screenshots/calibration.png)

### Allarme Postura
![Alert](docs/screenshots/posture_alert1.png)
![Alert](docs/screenshots/posture_alert2.png)

### Notifica allarme
![Notification](docs/screenshots/notification_alert1.jpeg)
![Notification](docs/screenshots/notification_alert2.jpeg)

### System Tray
![System Tray](docs/screenshots/system_tray1.jpeg)
![System Tray](docs/screenshots/system_tray2.jpeg)

</div>

🤝 Contributing

Contributi, segnalazioni di bug e richieste di funzionalità sono benvenuti. Si prega di consultare le Issue Templates prima di aprire una nuova segnalazione.

Developed by AntDF87 - Engineering & Biomedical Solutions





