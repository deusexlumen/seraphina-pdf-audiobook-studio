# AGENTS.md – Seraphina PDF Audiobook Studio

Diese Datei enthält alles, was ein KI-Coding-Agent über dieses Projekt wissen muss.

---

## Projekt-Überblick

**Seraphina PDF Audiobook Studio** ist ein Windows-Desktop-Tool, das PDF-Dokumente in MP3-Hörbücher umwandelt. Es nutzt Microsofts Edge-TTS für hochwertige deutsche Stimmen (Seraphina, Florian, Katja, Amala, Conrad) und bietet intelligente Textbereinigung, die PDF-typische Formatierungsprobleme (unnatürliche Zeilenumbrüche, Aufzählungen, URLs, Tausenderpunkte) für flüssiges Vorlesen korrigiert.

Das Projekt ist explizit für Nutzer mit wenig RAM optimiert (ab 4GB) und enthält mehrere Ausführungsmodi:
- **Normal-Modus** (`gui_smart.py`): Schnelle Verarbeitung, alles auf einmal im RAM.
- **Eco-Modus** (`gui_smart.py` + `smart_engine.py`): Seitenweise Verarbeitung mit Speicher-Freigabe.
- **Ultra-Light** (`ultra_light.py`): Keine GUI, extreme RAM-Einsparung für 2-4GB PCs.

---

## Technologie-Stack

- **Sprache:** Python 3.8+
- **GUI:** Standard `tkinter` (kein customtkinter im aktiven Code, obwohl in `requirements.txt` gelistet)
- **PDF-Parsing:** PyMuPDF (`fitz`)
- **TTS:** `edge-tts` (Online-Dienst, erfordert Internetverbindung)
- **Audio-Verarbeitung:** `pydub` (in `requirements.txt`), FFmpeg (optional, für Chunk-Konkatenation)
- **RAM-Erkennung:** `psutil` (wird in `smart_engine.py` on-demand importiert)

### Abhängigkeiten

Definiert in `requirements.txt`:
```
edge-tts>=6.1.0
PyMuPDF>=1.23.0
pydub>=0.25.1
customtkinter>=5.2.0
```

Installieren mit:
```bash
pip install -r requirements.txt
```

---

## Projektstruktur

```
seraphina-pdf-audiobook-studio-main/
├── START.bat              # Startet die Smart-GUI (gui_smart.py)
├── ULTRA.bat              # Startet den Ultra-Light CLI-Modus
├── gui_smart.py           # Haupt-GUI mit RAM-Check, Eco-Modus, Presets
├── gui_simple.py          # Ältere, einfachere GUI-Variante (Fallback)
├── smart_engine.py        # Kern-Engine: Normal- vs. Eco-Modus, Audio-Generierung
├── text_cleaner.py        # Textbereinigung: Zeilenumbrüche, URLs, Zahlen, Listen
├── pdf_parser.py          # Intelligenter PDF-Parser mit Layout-Erkennung
├── ssml_generator.py      # Experimenteller SSML-Generator für Prosody/Emotionen
├── tts_engine.py          # Ältere TTS-Engine-Klasse (EdgeTTSEngine)
├── ultra_light.py         # CLI-Notfallmodus für sehr schwache PCs
├── requirements.txt       # Python-Abhängigkeiten
├── README.md              # Englische Dokumentation
├── README_DE.md           # Deutsche Dokumentation
├── CONTRIBUTING.md        # Beitragsrichtlinien
├── LICENSE                # MIT-Lizenz
└── AGENTS.md              # Diese Datei
```

### Modul-Zuständigkeiten

| Modul | Aufgabe |
|-------|---------|
| `gui_smart.py` | Haupt-UI. Enthält `SeraphinaSmartGUI`. Deutsche Oberfläche, Presets (ADHD, Akademisch, Schnell, Langsam), Live-Vorschau, RAM-Warnung. |
| `smart_engine.py` | `SmartTTSEngine`. Orchestriert PDF-Parsing, Textbereinigung, Chunking, TTS-Generierung und Audio-Zusammenführung. |
| `pdf_parser.py` | `PDFIntelligentParser`. Extrahiert Textblöcke aus PDFs, klassifiziert sie (Header, Footer, Fußnote, Titel, Haupttext) und filtert irrelevante Elemente. |
| `text_cleaner.py` | `TextCleaner`. Der wichtigste Algorithmus für das Projekt. Verbindet gebrochene Sätze, ersetzt Aufzählungen durch natürliche Sprache, bereinigt URLs und Zahlen. |
| `ssml_generator.py` | `IntelligentSSMLGenerator`. Experimentell. Fügt `<prosody>`-Tags basierend auf Satztyp und Keyword-Emotionen hinzu. |
| `tts_engine.py` | `EdgeTTSEngine`. Frühere Engine-Implementierung mit eigenem Chunking und FFmpeg-Fallback. |
| `ultra_light.py` | Seitenweise CLI-Verarbeitung ohne GUI-Overhead. Kombiniert MP3-Dateien rein in Python (Datei-Anhängen), ohne FFmpeg. |

---

## Starten der Anwendung

### Haupt-GUI (empfohlen)
Doppelklick oder Kommandozeile:
```bash
START.bat
# oder direkt:
python gui_smart.py
```

### Ultra-Light (Notfallmodus)
```bash
ULTRA.bat
# oder direkt:
python ultra_light.py
```

### Simple GUI (Fallback)
```bash
python gui_simple.py
```

---

## Architektur-Details

### Verarbeitungsmodi

1. **Normal-Modus** (`_convert_normal` in `smart_engine.py`):
   - Extrahiert den gesamten PDF-Text auf einmal.
   - Wendet `TextCleaner` und optional SSML an.
   - Teilt in Chunks (Standard 4000 Zeichen) an Satzgrenzen.
   - Generiert Audio-Chunk für Chunk und fügt sie mit FFmpeg zusammen.

2. **Eco-Modus** (`_convert_eco` in `smart_engine.py`):
   - Öffnet das PDF seitenweise (`fitz.open`).
   - Pro Seite: Text extrahieren → bereinigen → Audio generieren → `gc.collect()`.
   - Am Ende: Alle Seiten-MP3s mit FFmpeg konkatenieren.
   - Wird automatisch bei < 6GB RAM empfohlen.

3. **Ultra-Light** (`ultra_light.py`):
   - Keine GUI, minimale Imports.
   - Erstellt pro Seite sofort eine MP3-Datei auf der Festplatte.
   - Kombiniert finale MP3 durch reines Python-Datei-Schreiben (`outfile.write(infile.read())`).
   - Kein FFmpeg nötig.

### Audio-Zusammenführung

Alle Modi verwenden temporäre Verzeichnisse. Die bevorzugte Zusammenführungsmethode ist **FFmpeg concat** (`-f concat -safe 0 -i list.txt -c copy`).
Falls FFmpeg nicht verfügbar ist, gibt es immer einen **Fallback auf den ersten Chunk** (`shutil.copy`).

### Stimmen-Definition

Stimmen sind als Dictionary in mehreren Dateien hartcodiert:
- `smart_engine.py`: `SmartTTSEngine.VOICES`
- `tts_engine.py`: `EdgeTTSEngine.VOICES`
- `gui_simple.py`: `voice_map`
- `ultra_light.py`: `voices`

**Bei Stimmen-Änderungen müssen alle vier Orte synchronisiert werden.**

---

## Code-Stil & Konventionen

- **PEP 8** ist das Ziel (siehe `CONTRIBUTING.md`).
- **Docstrings** werden für öffentliche Funktionen erwartet.
- **Kommentare** sind auf **Deutsch** verfasst – dies gilt für alle Dateien.
- **Variable- und Funktionsnamen** sind meist auf Deutsch oder Englisch gemischt (z. B. `speaking_rate`, ` bereinige_text`, `chunk_dateien`).
- **UI-Text** ist komplett auf Deutsch.
- **`if __name__ == "__main__"`**-Blöcke enthalten in fast jeder Datei einen kleinen Selbsttest.

### Wichtige Konventionen beim Editieren

- **Textbereinigung ist der Kernwert des Projekts.** Änderungen an `text_cleaner.py` sollten minimal und wohlbedacht sein, da sie die Lesbarkeit direkt beeinflussen.
- **RAM-Effizienz hat Priorität.** Vermeide das Laden ganzer PDFs in den Speicher, wenn du im Eco/Ultra-Kontext arbeitest.
- **FFmpeg ist optional.** Jede Audio-Konkatenation muss einen Fallback ohne FFmpeg haben.
- **Async/Threading:** Die GUI startet die Konvertierung immer in einem `threading.Thread`, um tkinter nicht zu blockieren. Innerhalb des Threads wird `asyncio.run()` für `edge_tts` aufgerufen.

---

## Testing

**Das Projekt hat aktuell kein formales Test-Framework** (kein `pytest`, kein `tests/`-Ordner).

Validierung erfolgt über:
1. **`if __name__ == "__main__"`-Blöcke** in jeder Python-Datei.
2. **Manuelle GUI-Tests** mit echten PDFs.

Wenn du Tests hinzufügst, solltest du:
- Einen `tests/`-Ordner anlegen.
- `pytest` als Dev-Dependency dokumentieren.
- Unit-Tests für `TextCleaner` und `PDFIntelligentParser` priorisieren, da diese die komplexeste Logik enthalten.

---

## Bekannte Schwächen & Hinweise

- **Keine zentrale Konfiguration:** Stimmen, Chunk-Größen und Pfade sind über mehrere Dateien verteilt hartcodiert.
- **Fehlerhafte Preset-Methoden:** In `gui_smart.py` verweisen die Presets (`apply_adhd_preset`, etc.) teilweise auf `self.include_headers`, das Attribut existiert aber nicht (es heißt `self.remove_headers`). Das führt zu einem `AttributeError`, wenn diese Presets geklickt werden.
- **gui_smart.py importiert `fitz` nur im `__main__`-Block**, nutzt es aber in `analyze()` ohne expliziten Import am Modul-Level. Das funktioniert nur, weil `fitz` indirekt über `smart_engine.py` oder `pdf_parser.py` im Speicher sein kann, ist aber unsauber.
- **FFmpeg-Fallback kopiert nur den ersten Chunk**, statt alle Chunks zusammenzuführen. Das führt bei langen Dokumenten zu Datenverlust, wenn FFmpeg fehlt.
- **Ultra-Light fügt MP3-Dateien binär an.** Das funktioniert bei MP3s meist, ist aber kein standardskonformes Muxing.

---

## Sicherheitshinweise

- **Temporäre Dateien:** Die Engines erstellen temporäre Verzeichnisse (`tempfile.mkdtemp()` oder lokale `temp_ultra/`-Ordner). Diese werden in `cleanup()` oder am Ende des Prozesses gelöscht, aber bei einem Crash können sie zurückbleiben.
- **Input-Validierung:** Es gibt kaum Pfad-Validierung. Übergaben an `subprocess.run()` für FFmpeg sind lokal kontrolliert (keine User-Input-Injection in die FFmpeg-Argumente).
- **Online-Abhängigkeit:** `edge-tts` kommuniziert mit Microsofts Online-Servern. Es werden keine API-Keys benötigt, aber eine Internetverbindung ist zwingend erforderlich.

---

## Deployment

Es gibt keinen automatisierten Build- oder Release-Prozess. Das Projekt wird als Quellcode-Repository verteilt. Endanwender führen `START.bat` aus.

Geplante, aber noch nicht umgesetzte Deployment-Ziele (siehe `CONTRIBUTING.md`):
- Windows-Installer mit Inno Setup oder NSIS.
- Standalone-EXE mittels PyInstaller (nicht im Repo vorhanden).

---

## Lizenz

MIT License – frei für private und kommerzielle Nutzung.
