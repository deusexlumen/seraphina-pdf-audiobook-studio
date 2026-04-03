# 🎙️ Seraphina PDF Audiobook Studio

**Convert PDFs to audiobooks with smart text cleaning.**  
Works on any PC - from high-end to 4GB RAM laptops.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Windows](https://img.shields.io/badge/Windows-10%2F11-lightblue.svg)](https://microsoft.com)

[🇩🇪 Deutsche Version](README_DE.md)

---

## ✨ Why This Tool?

**The Problem:** PDF readers pause at every line break:
```
"Hast du dich jemals
gefragt, wie das
funktioniert?"
```
☠️ **Your brain:** "Make it stop!"

**Our Solution:** Smart text cleaning joins broken sentences:
```
"Hast du dich jemals gefragt, wie das funktioniert?"
```
🧠 **Your brain:** "Ah, much better!"

---

## 🚀 Quick Start

### 1. Install
```bash
pip install -r requirements.txt
```

### 2. Run
Double-click `START.bat`

### 3. Convert
1. Select PDF
2. Choose voice (Seraphina recommended)
3. The app **automatically detects** your RAM and suggests Eco-mode if needed
4. Click "Convert to MP3"
5. Done! 🎉

---

## 💻 Smart RAM Detection

**The app automatically adapts to your PC:**

| Your PC | What Happens | Mode |
|---------|--------------|------|
| 8GB+ RAM | Fast processing, everything at once | Normal |
| 4-6GB RAM | Page-by-page, memory efficient | Eco (auto) |
| 2-4GB RAM | Emergency mode available | Ultra-Light |

**You can always override:** Just check/uncheck "Eco-Mode" in the settings.

### 🆘 Still crashing? Use Ultra-Light!
For very old PCs with 2-4GB RAM that can't even run the GUI:
```bash
ULTRA.bat  # No GUI, extreme memory saving
```

---

## 🎤 Features

| Feature | Description |
|---------|-------------|
| 🧠 **Smart Cleaning** | Removes unnatural line breaks, fixes broken sentences |
| 📋 **List Fixer** | Turns `a)`, `1.` bullets into natural speech: "firstly, secondly..." |
| 🔗 **URL Cleaner** | Reads URLs as "Link to example.com" instead of "h-t-t-p-s..." |
| 🔢 **Number Fixer** | Removes thousand-separators so numbers are read correctly |
| 🎛️ **Voice Control** | Adjust speed, pitch, and volume |
| 👁️ **Live Preview** | Preview cleaned text before generating audio |
| ⚡ **Presets** | ADHD-Mode, Academic, Fast, Slow — one-click settings |
| 💾 **Auto RAM Adapt** | Automatically chooses best processing mode |
| 🎙️ **Edge TTS** | High-quality voices (Seraphina, Katja, Florian...) |
| 📄 **PDF Intelligence** | Auto-removes headers, footers, page numbers |
| 🎵 **MP3 Export** | Direct audio file output |
| ⛔ **Cancel Anytime** | Abort conversion mid-process |
| 🔧 **No FFmpeg Required** | Falls back to Python-only audio joining |

---

## 🎤 Voices

| Voice | Language | Quality |
|-------|----------|---------|
| **Seraphina** 🇩🇪 | German | ⭐⭐⭐⭐⭐ |
| Katja 🇩🇪 | German | ⭐⭐⭐⭐ |
| Amala 🇩🇪 | German | ⭐⭐⭐⭐ |
| Florian 🇩🇪 | German | ⭐⭐⭐⭐⭐ |
| Conrad 🇩🇪 | German | ⭐⭐⭐⭐ |

---

## 📂 Files

```
seraphina-pdf-audiobook-studio/
├── START.bat              # 🚀 Double-click this!
├── ULTRA.bat              # Emergency CLI mode for old PCs
├── gui_smart.py           # Smart GUI with RAM detection
├── smart_engine.py        # Core engine (Normal + Eco mode)
├── text_cleaner.py        # Text preprocessing
├── pdf_parser.py          # PDF extraction
├── ssml_generator.py      # Voice emotion & prosody tags
├── tts_engine.py          # Edge-TTS integration
├── voices.py              # Central voice configuration
├── tests/                 # Unit tests
├── requirements.txt       # Dependencies
├── README.md              # This file (English)
└── README_DE.md           # German version
```

**Just 1 file to start:** `START.bat` 🎯

---

## ⚠️ Requirements

- Windows 10/11
- Python 3.8+
- Internet connection (Edge TTS is online)
- **RAM:** Works with 4GB+ (auto-adapts)
- Optional: FFmpeg (for better audio joining)

---

## 🧪 Tests

Run the unit tests:
```bash
python -m unittest tests.test_text_cleaner
```

---

## 📝 License

MIT License - Free for personal and commercial use.

---

**Made for people who think differently** 🧠✨
