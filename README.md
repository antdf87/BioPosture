BioPosture: Markerless Kinematic Analysis System

Engineering Release: v2.0.0 (Multi-OS Support)
Author: Ing. AntDF87
Domain: Biomedical Engineering / Ergonomics / Computer Vision
License: MIT License

📋 Abstract Tecnico

BioPosture è una piattaforma software cross-platform progettata per l'analisi cinematica in tempo reale e il monitoraggio ergonomico del rachide cervicale. Sfruttando algoritmi di Computer Vision e reti neurali per la stima della posa (MediaPipe Framework), il sistema elabora un flusso video per quantificare vettori geometrici chiave (inclinazione testa-collo, simmetria scapolare, distanza focale) senza l'ausilio di sensori indossabili (markerless).



⚙️ Architettura del Sistema

Il software è sviluppato in Python e implementa una pipeline di elaborazione così strutturata:

Acquisizione: Interfacciamento hardware con dispositivi di acquisizione ottica (OpenCV).

Inference: Estrazione dei landmark facciali e corporei (Pose/Face Mesh Topology).

Analisi Geometrica: Calcolo in tempo reale degli angoli di Eulero e vettori di distanza normalizzati sull'iride.

HMI: Interfaccia grafica High-DPI basata su customtkinter con rendering vettoriale.



🚀 Funzionalità Ingegneristiche

Real-Time Pose Estimation: Monitoraggio continuo con latenza minima (<30ms).

Analisi Biometrica:

Cervical Tilt Assessment (Analisi inclinazione laterale).

Scapular Symmetry (Rilevamento dislivelli posturali).

Screen Distance Estimation (Calcolo prossimità basato su calibrazione iridea).

Adaptive Notification System: Feedback acustico/visivo basato su soglie di tolleranza configurabili.

Background Process: Esecuzione ottimizzata in System Tray per minimizzare l'impatto sulla CPU.

Data Logging: Esportazione delle metriche temporali in formato CSV per post-processing.



🛠 Deployment & Installazione

Eseguibile Standalone (Consigliata)

Scaricare l'ultima release dalla sezione Releases di questa repository.

Eseguire l'installer specifico per il proprio OS (.exe per Windows, .dmg per macOS).

Al primo avvio, seguire la procedura di Calibrazione Biometrica (durata: 5s).

Esecuzione da Codice Sorgente (Dev)

Requisiti: Python 3.10+

pip install -r requirements.txt
python bioposture_interface.py



💻 Requisiti di Sistema

OS: Windows 10/11, macOS (Silicon/Intel), Linux.

Input: Webcam integrata o USB (risoluzione min. 720p).

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
![Notification](docs/screenshots/notification_alert1.png)
![Notification](docs/screenshots/notification_alert2.png)

### Notifica allarme
![System Tray](docs/screenshots/system_tray1.png)
![System Tray](docs/screenshots/system_tray2.png)

</div>

Runtime: Architettura 64-bit, 4GB RAM.


Developed by AntDF87 - Engineering & Biomedical Solutions

