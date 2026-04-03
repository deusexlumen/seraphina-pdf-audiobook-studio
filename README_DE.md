# 🎙️ Seraphina PDF Audiobook Studio

**PDFs in Hörbücher verwandeln – mit intelligentem Text-Cleaning.**  
Funktioniert auf jedem PC – vom High-End bis zum 4GB-Laptop.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Windows](https://img.shields.io/badge/Windows-10%2F11-lightblue.svg)](https://microsoft.com)

[🇬🇧 English Version](README.md)

---

## ✨ Warum dieses Tool?

**Das Problem:** PDF-Reader machen bei jedem Zeilenumbruch eine Pause:
```
"Hast du dich jemals
gefragt, wie das
funktioniert?"
```
☠️ **Dein Gehirn:** „Hör auf!“

**Unsere Lösung:** Intelligentes Text-Cleaning verbindet Sätze:
```
"Hast du dich jemals gefragt, wie das funktioniert?"
```
🧠 **Dein Gehirn:** „Ah, viel besser!“

---

## 🚀 Schnellstart

### 1. Installieren
```bash
pip install -r requirements.txt
```

### 2. Starten
Doppelklicke `START.bat`

### 3. Konvertieren
1. PDF auswählen
2. Stimme wählen (Seraphina empfohlen)
3. Die App **erkennt automatisch** deinen RAM und schlägt Eco-Modus vor
4. „In MP3 konvertieren“ klicken
5. Fertig! 🎉

---

## 💻 Intelligente RAM-Erkennung

**Die App passt sich automatisch an deinen PC an:**

| Dein PC | Was passiert | Modus |
|---------|--------------|-------|
| 8GB+ RAM | Schnelle Verarbeitung, alles auf einmal | Normal |
| 4-6GB RAM | Seitenweise, speicherschonend | Eco (auto) |
| 2-4GB RAM | Notfall-Modus verfügbar | Ultra-Light |

**Du kannst jederzeit überschreiben:** Einfach „Eco-Modus" an-/ausschalten.

### 🆘 Trotzdem Abstürze? Ultra-Light nutzen!
Für sehr alte PCs mit 2-4GB RAM, die nicht mal die GUI schaffen:
```bash
ULTRA.bat  # Keine GUI, extrem speichersparend
```

---

## 🎤 Funktionen

| Funktion | Beschreibung |
|----------|--------------|
| 🧠 **Smart Cleaning** | Entfernt unnatürliche Zeilenumbrüche, repariert Sätze |
| 📋 **Aufzählungen fixen** | Macht aus `a)`, `1.` natürliche Sprache: „erstens, zweitens...“ |
| 🔗 **URLs bereinigen** | Sagt „Link zu example.com“ statt „h-t-t-p-s..." |
| 🔢 **Zahlen fixen** | Entfernt Tausenderpunkte, damit Zahlen korrekt vorgelesen werden |
| 🎛️ **Stimmen-Steuerung** | Geschwindigkeit, Stimmlage (Pitch) und Lautstärke einstellbar |
| 👁️ **Live-Vorschau** | Bereinigten Text vor der Audio-Erzeugung ansehen |
| ⚡ **Presets** | ADHD-Modus, Akademisch, Schnell, Langsam – mit einem Klick |
| 💾 **Auto RAM Adapt** | Wählt automatisch den besten Modus |
| 🎙️ **Edge TTS** | Hochwertige Stimmen (Seraphina, Katja...) |
| 📄 **PDF-Intelligenz** | Entfernt automatisch Kopf-/Fußzeilen |
| 🎵 **MP3-Export** | Direkte Audio-Ausgabe |
| ⛔ **Jederzeit abbrechen** | Konvertierung läuft nicht mehr unkontrolliert |
| 🔧 **Kein FFmpeg nötig** | Python-only Fallback für Audio-Zusammenführung |

---

## 🎤 Stimmen

| Stimme | Sprache | Qualität |
|--------|---------|----------|
| **Seraphina** 🇩🇪 | Deutsch | ⭐⭐⭐⭐⭐ |
| Katja 🇩🇪 | Deutsch | ⭐⭐⭐⭐ |
| Amala 🇩🇪 | Deutsch | ⭐⭐⭐⭐ |
| Florian 🇩🇪 | Deutsch | ⭐⭐⭐⭐⭐ |
| Conrad 🇩🇪 | Deutsch | ⭐⭐⭐⭐ |

---

## 📂 Dateien

```
seraphina-pdf-audiobook-studio/
├── START.bat              # 🚀 Doppelklick hier!
├── ULTRA.bat              # Notfall-CLI-Modus für alte PCs
├── gui_smart.py           # Smarte GUI mit RAM-Erkennung
├── smart_engine.py        # Engine (Normal + Eco)
├── text_cleaner.py        # Text-Bereinigung
├── pdf_parser.py          # PDF-Extraktion
├── ssml_generator.py      # Stimm-Emotionen & Prosody
├── tts_engine.py          # Edge-TTS-Integration
├── voices.py              # Zentrale Stimmen-Konfiguration
├── tests/                 # Unit-Tests
├── requirements.txt       # Abhängigkeiten
├── README_DE.md           # Diese Datei (Deutsch)
└── README.md              # Englische Version
```

**Nur 1 Datei zum Starten:** `START.bat` 🎯

---

## ⚠️ Voraussetzungen

- Windows 10/11
- Python 3.8+
- Internet-Verbindung (Edge TTS ist online)
- **RAM:** Funktioniert mit 4GB+ (passt sich automatisch an)
- Optional: FFmpeg (für bessere Audio-Verarbeitung)

---

## 🧪 Tests

Unit-Tests ausführen:
```bash
python -m unittest tests.test_text_cleaner
```

---

## 💡 Für ADHS-Hirne

> „Dein Gehirn ist nicht kaputt. PDF-Reader sind nur für neurotypische Menschen gemacht. Dieses Tool behebt das.“

Wenn dir das Tool hilft, gib uns einen Stern ⭐ auf GitHub!

---

## 📝 Lizenz

MIT License – Frei für private und kommerzielle Nutzung.

---

**Gemacht für Menschen, die anders denken** 🧠✨
