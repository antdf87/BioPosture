BioPosture v2.0.0: Sistema di Analisi Cinematica Markerless per l'Ergonomia Computazionale
Relazione Tecnica di Progetto Autore: AntDF87 Dominio: Ingegneria Biomedica / Human-Machine Interface (HMI)
1. Abstract e Razionale del Progetto
BioPosture si configura come una piattaforma software cross-platform avanzata per il monitoraggio preventivo e la correzione dei disturbi muscolo-scheletrici (DMS) correlati all'utilizzo prolungato dei Video Terminali (VDT). Il progetto nasce dalla necessità di mitigare l'incidenza di patologie quali la "Text Neck Syndrome" e la sindrome del tunnel carpale, sempre più prevalenti nell'era del lavoro ibrido. L'obiettivo primario è fornire uno strumento di analisi cinematica in tempo reale del rachide cervicale e del cingolo scapolare senza l'ausilio di sensori indossabili (approccio markerless), superando i limiti di costo e invasività delle soluzioni hardware dedicate (es. gilet aptici o IMU sensorizzati).
Il sistema integra algoritmi di Computer Vision e reti neurali convoluzionali (CNN) per trasformare una comune webcam consumer in un sensore biometrico di precisione, chiudendo il loop di feedback con l'utente tramite stimoli visivi e acustici immediati per indurre una neuro-modulazione della postura.
2. Architettura del Sistema
L'architettura software è rigorosamente modulare, sviluppata in Python (v3.10+) e segue il pattern architetturale Event-Driven. Il sistema è progettato per garantire un throughput elevato con una latenza di elaborazione <30ms per frame su CPU standard (senza accelerazione GPU dedicata).
2.1 Pipeline di Elaborazione (Data Flow)
Il flusso dati è orchestrato attraverso quattro stadi logici distinti:
1.	Acquisizione (Input Layer):
o	Il sottosistema di I/O utilizza la libreria OpenCV per l'interfacciamento hardware.
o	Su ambiente Windows, viene forzato il backend CAP_DSHOW (DirectShow) per minimizzare il tempo di inizializzazione della periferica.
o	Il frame viene acquisito in formato BGR e convertito in RGB per l'elaborazione neurale. Viene applicato un ridimensionamento dinamico (scale factor) per mantenere l'aspect ratio originale ottimizzando al contempo il carico computazionale.
2.	Inferenza Neurale (Processing Layer):
o	Il core di visione artificiale si basa sul framework MediaPipe (Google), scelto per la sua architettura leggera ottimizzata per l'inferenza su CPU mobile/desktop.
o	Face Mesh Topology: Estrazione di 468 landmark tridimensionali del volto. In particolare, vengono tracciati i punti iridei (468, 473) con precisione sub-pixel per la stima della profondità.
o	Pose Topology (BlazePose): Utilizzo del modello Pose Landmarker per mappare 33 keypoint corporei. Il modello opera con una confidence threshold del 60% per filtrare falsi positivi in ambienti con illuminazione sub-ottimale.
3.	Calcolo Geometrico & Signal Processing (Logic Layer):
o	I landmark cartesiani normalizzati $(x, y, z)$ vengono proiettati nello spazio immagine per il calcolo vettoriale.
o	Smoothing Algorithm: Per mitigare il rumore ad alta frequenza ("jitter") intrinseco alla stima ottica, viene applicato un filtro Exponential Moving Average (EMA) sui dati grezzi: 
$$S_t = \alpha \cdot Y_t + (1 - \alpha) \cdot S_{t-1}$$
Dove $S_t$ è il valore levigato corrente, $Y_t$ è la misura grezza, e $\alpha$ è il fattore di smoothing (configurato dinamicamente tra 0.7 e 0.8 per bilanciare reattività e stabilità).
4.	Interfaccia Utente (HMI Layer):
o	Il rendering grafico è affidato alla libreria CustomTkinter, che permette la creazione di GUI vettoriali moderne con supporto nativo per High-DPI scaling (Windows/macOS).
o	Il ciclo di aggiornamento della UI è disaccoppiato dal thread di elaborazione video per evitare fenomeni di "freezing" dell'interfaccia durante picchi di carico CPU.
3. Metodologia di Analisi Biometrica
Il core ingegneristico di BioPosture quantifica lo stato ergonomico attraverso tre vettori fisiologici critici, confrontati in tempo reale con una Baseline calibrata.
A. Cervical Tilt Assessment (Inclinazione Laterale)
Il sistema calcola l'angolo di rollio della testa analizzando il vettore che congiunge i lobi auricolari (landmark Tragus sinistro e destro).
•	Formula: L'inclinazione $\theta$ è derivata dall'arcotangente delle coordinate $y$ e $x$ dei landmark auricolari (punti 7 e 8 della topologia MediaPipe).
•	Significato Clinico: Una deviazione angolare persistente >10° indica una flessione laterale patologica, causa frequente di contratture unilaterali del muscolo trapezio superiore e sternocleidomastoideo.
B. Scapular Symmetry (Dismetria del Cingolo Scapolare)
Viene analizzato il dislivello sull'asse Y tra i due acromion (spalle, landmark 11 e 12).
•	Logica: L'algoritmo rileva elevazioni asimmetriche (es. postura da "telefono all'orecchio" o appoggio sbilanciato sui braccioli della sedia).
•	Soglia Adattiva: La sensibilità di rilevazione è modulata da un parametro di "Severity" configurabile dall'utente, che scala le soglie di tolleranza in base alla riabilitazione necessaria.
C. Screen Distance Estimation (Prossimità Relativa)
In assenza di sensori di profondità (Time-of-Flight o LiDAR), la coordinata $z$ (profondità) viene stimata tramite un modello geometrico basato sulla dimensione apparente dell'iride.
•	Algoritmo: Il sistema calcola il diametro euclideo dell'iride in pixel. Durante la calibrazione, viene salvato un valore di riferimento ($D_{ref}$). La distanza relativa è calcolata come ratio $R = D_{curr} / D_{ref}$.
•	Prevenzione Astenopia: Se $R > 1.35$ (utente troppo vicino) o $R < 0.65$ (troppo lontano), il sistema segnala un rischio di astenopia accomodativa (affaticamento visivo e convergenza forzata).
4. Analisi HMI (Human-Machine Interface)
L'interfaccia è stata progettata seguendo i principi di Cognitive Ergonomics, mirando a massimizzare la consapevolezza situazionale minimizzando al contempo il carico cognitivo e l'interruzione del flusso di lavoro (Flow State).
4.1 Strategia di Feedback Multimodale
Il sistema non si limita al monitoring passivo, ma implementa un feedback loop attivo:
•	Feedback Visivo (Semantica del Colore):
o	Verde/Ciano: Stato di omeostasi posturale (entro le soglie di tolleranza).
o	Arancione: Warning pre-allerta (deviazione transitoria).
o	Rosso: Alert critico (deviazione persistente oltre il tempo_allarme).
•	Feedback Periferico (System Tray): L'applicazione è progettata per ridursi nella barra delle applicazioni ("Tray Icon"), cambiando dinamicamente il colore dell'icona (Verde/Rossa) per fornire uno stato periferico senza occupare spazio schermo.
4.2 Adaptive Notification System
Per evitare il fenomeno della Notification Fatigue (desensibilizzazione agli allarmi), il sistema utilizza un algoritmo intelligente di cooldown:
1.	Viene rilevato un errore posturale.
2.	Si avvia un timer di tolleranza (es. 5 secondi).
3.	Se l'errore persiste allo scadere del timer, viene generata una notifica OS nativa (Toast/Banner).
4.	Successive notifiche vengono inibite per un periodo di cooldown (es. 8 secondi) per permettere all'utente di correggersi senza stress acustico continuo.
4.3 Procedura di Calibrazione (User-Centered Design)
Riconoscendo la variabilità antropometrica (altezza, larghezza spalle, distanza monitor), BioPosture non utilizza costanti fisse.
•	Algoritmo di Zeroing: Una procedura guidata acquisisce un buffer di frame per 5 secondi mentre l'utente assume la postura ergonomica ideale.
•	Calcolo Baseline: Vengono calcolate le medie statistiche dei vettori biometrici nel buffer, stabilendo lo "zero fisiologico" personalizzato dell'utente.
5. Deployment, Persistenza e Ingegneria del Software
Il progetto rispetta gli standard rigorosi dell'ingegneria del software moderna per garantire affidabilità e manutenibilità.
•	Cross-Platform Deployment:
o	Utilizzo di PyInstaller per generare eseguibili frozen (.exe per Windows, .app/dmg per macOS, binari ELF per Linux).
o	Ottimizzazione --noupx su Windows per ridurre i tempi di decompressione in memoria all'avvio.
o	Gestione dei percorsi nativi per le risorse (icone) sia in modalità sviluppo che in modalità frozen (sys._MEIPASS).
•	Configuration Management:
o	La persistenza dello stato (preferenze, soglie di calibrazione) è gestita tramite serializzazione JSON.
o	Il ConfigManager implementa logiche di Deep Merging per garantire la compatibilità retroattiva delle configurazioni durante gli aggiornamenti software.
•	Autostart Management:
o	Moduli specifici per la gestione dell'avvio automatico su ogni OS: Registro di sistema (Windows), LaunchAgents (macOS), Desktop Entries XDG (Linux).
6. Conclusioni e Sviluppi Futuri
BioPosture v2.0.0 dimostra l'efficacia dell'applicazione di tecnologie di visione artificiale consumer in ambito preventivo e occupazionale. Il sistema offre una soluzione a basso costo, scalabile e non invasiva, rispondendo concretamente alle esigenze di salute digitale (Digital Health) nell'era dello smart working.
Gli sviluppi futuri prevedono l'integrazione di analisi predittiva basata su serie storiche per identificare trend di degradazione posturale durante la giornata lavorativa e suggerire pause attive mirate.

