#!/usr/bin/env python3
"""
Seraphina Smart GUI - Mit RAM-Check und Eco-Modus
Eine GUI für alle PCs - passt sich automatisch an
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import asyncio
from pathlib import Path
import fitz

from smart_engine import SmartTTSEngine
from pdf_parser import PDFIntelligentParser
from text_cleaner import TextCleaner


class SeraphinaSmartGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Seraphina PDF zu MP3 - Smart")
        self.root.geometry("750x850")
        self.root.minsize(750, 850)
        
        # RAM-Check beim Start
        self.ram_gb = SmartTTSEngine.detect_ram()
        self.eco_recommended = SmartTTSEngine.should_use_eco_mode()
        
        # Variablen
        self.pdf_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.selected_voice = tk.StringVar(value="Seraphina")
        self.use_eco_mode = tk.BooleanVar(value=self.eco_recommended)
        
        # Neue Prosody-Variablen
        self.speaking_rate = tk.StringVar(value="normal")
        self.pitch = tk.StringVar(value="normal")
        self.volume = tk.StringVar(value="normal")
        
        # Neue Bereinigungs-Variablen
        self.url_mode = tk.StringVar(value="Domain anzeigen")
        self.clean_lists = tk.BooleanVar(value=True)
        self.fix_quotes = tk.BooleanVar(value=True)
        self.fix_thousands = tk.BooleanVar(value=True)
        self.remove_headers = tk.BooleanVar(value=True)
        self.include_footnotes = tk.BooleanVar(value=False)
        self.use_ssml = tk.BooleanVar(value=False)
        self.chunk_size = tk.IntVar(value=4000)
        
        self.status = tk.StringVar(value="Bereit")
        self.progress = tk.DoubleVar(value=0)
        self.is_converting = False
        self.cancel_requested = threading.Event()
        
        self.build_ui()
        
        # RAM-Warnung zeigen wenn nötig
        if self.eco_recommended:
            self.root.after(500, self._show_ram_warning)
    
    def build_ui(self):
        # Hauptframe mit Scrollbar-Unterstützung
        container = tk.Frame(self.root)
        container.pack(fill="both", expand=True)
        
        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.main_frame = tk.Frame(canvas, padx=20, pady=15)
        
        self.main_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.main_frame, anchor="nw", width=730)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Maus-Scroll für Canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind("<MouseWheel>", _on_mousewheel)
        
        # Titel
        tk.Label(self.main_frame, text="🎙️ Seraphina PDF zu MP3", 
                font=("Segoe UI", 20, "bold"), fg="#0078d4").pack()
        
        # RAM-Info
        ram_color = "#ff6b6b" if self.eco_recommended else "#51cf66"
        ram_text = f"RAM erkannt: {self.ram_gb:.1f} GB"
        if self.eco_recommended:
            ram_text += " (Eco-Modus empfohlen)"
        tk.Label(self.main_frame, text=ram_text, font=("Segoe UI", 9), 
                fg=ram_color).pack(pady=(0, 10))
        
        # PDF Auswahl
        self._create_pdf_section(self.main_frame)
        
        # Presets
        self._create_presets_section(self.main_frame)
        
        # Einstellungen
        self._create_settings_section(self.main_frame)
        
        # Textbereinigung
        self._create_cleanup_section(self.main_frame)
        
        # Erweitert
        self._create_advanced_section(self.main_frame)
        
        # Eco-Modus
        self._create_eco_section(self.main_frame)
        
        # Info-Log
        self._create_log_section(self.main_frame)
        
        # Fortschritt
        self._create_progress_section(self.main_frame)
        
        # Buttons
        self._create_buttons(self.main_frame)
    
    def _create_pdf_section(self, parent):
        frame = tk.LabelFrame(parent, text="PDF Datei", font=("Segoe UI", 9, "bold"), 
                             padx=10, pady=10)
        frame.pack(fill="x", pady=5)
        
        row = tk.Frame(frame)
        row.pack(fill="x")
        
        tk.Entry(row, textvariable=self.pdf_path, font=("Segoe UI", 10), 
                width=50).pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        tk.Button(row, text="📁 Durchsuchen", command=self.browse_pdf,
                 bg="#0078d4", fg="white", cursor="hand2").pack(side="right")
    
    def _create_presets_section(self, parent):
        frame = tk.LabelFrame(parent, text="Schnell-Presets", font=("Segoe UI", 9, "bold"),
                             padx=10, pady=10)
        frame.pack(fill="x", pady=5)
        
        btn_frame = tk.Frame(frame)
        btn_frame.pack(fill="x")
        
        presets = [
            ("🧠 ADHD-Modus", self.apply_adhd_preset, "#ff922b"),
            ("📚 Akademisch", self.apply_academic_preset, "#339af0"),
            ("⚡ Schnell", self.apply_fast_preset, "#51cf66"),
            ("🐢 Langsam", self.apply_slow_preset, "#9775fa"),
        ]
        
        for text, cmd, color in presets:
            tk.Button(btn_frame, text=text, command=cmd,
                     bg=color, fg="white", font=("Segoe UI", 9),
                     cursor="hand2").pack(side="left", padx=5, expand=True, fill="x")
    
    def _create_settings_section(self, parent):
        frame = tk.LabelFrame(parent, text="Stimme & Tempo", font=("Segoe UI", 9, "bold"),
                             padx=10, pady=10)
        frame.pack(fill="x", pady=5)
        
        # Stimme
        tk.Label(frame, text="Stimme:", font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w", pady=3)
        voices = list(SmartTTSEngine.VOICES.keys())
        ttk.Combobox(frame, textvariable=self.selected_voice, values=voices,
                    state="readonly", width=30).grid(row=0, column=1, sticky="w", padx=5, pady=3)
        
        # Geschwindigkeit
        tk.Label(frame, text="Geschwindigkeit:", font=("Segoe UI", 10)).grid(row=1, column=0, sticky="w", pady=3)
        ttk.Combobox(frame, textvariable=self.speaking_rate,
                    values=["sehr langsam", "langsam", "normal", "schnell", "sehr schnell"],
                    state="readonly", width=30).grid(row=1, column=1, sticky="w", padx=5, pady=3)
        
        # Stimmlage
        tk.Label(frame, text="Stimmlage:", font=("Segoe UI", 10)).grid(row=2, column=0, sticky="w", pady=3)
        ttk.Combobox(frame, textvariable=self.pitch,
                    values=["tief", "normal", "hoch"],
                    state="readonly", width=30).grid(row=2, column=1, sticky="w", padx=5, pady=3)
        
        # Lautstärke
        tk.Label(frame, text="Lautstärke:", font=("Segoe UI", 10)).grid(row=3, column=0, sticky="w", pady=3)
        ttk.Combobox(frame, textvariable=self.volume,
                    values=["leise", "normal", "laut"],
                    state="readonly", width=30).grid(row=3, column=1, sticky="w", padx=5, pady=3)
        
        # Output
        tk.Label(frame, text="Speichern unter:", font=("Segoe UI", 10)).grid(row=4, column=0, sticky="w", pady=3)
        row = tk.Frame(frame)
        row.grid(row=4, column=1, sticky="we", padx=5, pady=3)
        tk.Entry(row, textvariable=self.output_path, font=("Segoe UI", 10), width=40).pack(side="left", fill="x", expand=True)
        tk.Button(row, text="Ändern", command=self.browse_output).pack(side="right", padx=(5, 0))
    
    def _create_cleanup_section(self, parent):
        frame = tk.LabelFrame(parent, text="Textbereinigung", font=("Segoe UI", 9, "bold"),
                             padx=10, pady=10)
        frame.pack(fill="x", pady=5)
        
        # URLs
        tk.Label(frame, text="URLs behandeln als:", font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w", pady=3)
        ttk.Combobox(frame, textvariable=self.url_mode,
                    values=["Domain anzeigen", "Nur 'Link' sagen", "Entfernen", "Original lassen"],
                    state="readonly", width=30).grid(row=0, column=1, sticky="w", padx=5, pady=3)
        
        # Checkboxes
        tk.Checkbutton(frame, text="Aufzählungen natürlich sprechen (erstens, zweitens…)",
                      variable=self.clean_lists, font=("Segoe UI", 10)).grid(row=1, column=0, columnspan=2, sticky="w", pady=2)
        tk.Checkbutton(frame, text="Anführungszeichen bereinigen",
                      variable=self.fix_quotes, font=("Segoe UI", 10)).grid(row=2, column=0, columnspan=2, sticky="w", pady=2)
        tk.Checkbutton(frame, text="Tausenderpunkte in Zahlen entfernen",
                      variable=self.fix_thousands, font=("Segoe UI", 10)).grid(row=3, column=0, columnspan=2, sticky="w", pady=2)
        tk.Checkbutton(frame, text="Header/Footer entfernen",
                      variable=self.remove_headers, font=("Segoe UI", 10)).grid(row=4, column=0, columnspan=2, sticky="w", pady=2)
        tk.Checkbutton(frame, text="Fußnoten einbeziehen",
                      variable=self.include_footnotes, font=("Segoe UI", 10)).grid(row=5, column=0, columnspan=2, sticky="w", pady=2)
    
    def _create_advanced_section(self, parent):
        frame = tk.LabelFrame(parent, text="Erweitert", font=("Segoe UI", 9, "bold"),
                             padx=10, pady=10)
        frame.pack(fill="x", pady=5)
        
        tk.Checkbutton(frame, text="SSML-Prosody verwenden (experimentell)",
                      variable=self.use_ssml, font=("Segoe UI", 10)).pack(anchor="w")
        
        chunk_frame = tk.Frame(frame)
        chunk_frame.pack(fill="x", pady=(5, 0))
        tk.Label(chunk_frame, text="Max. Zeichen pro Chunk:", font=("Segoe UI", 10)).pack(side="left")
        tk.Spinbox(chunk_frame, from_=1000, to=10000, increment=500,
                  textvariable=self.chunk_size, width=10, font=("Segoe UI", 10)).pack(side="left", padx=5)
    
    def _create_eco_section(self, parent):
        frame = tk.LabelFrame(parent, text="Leistung", font=("Segoe UI", 9, "bold"),
                             padx=10, pady=10)
        frame.pack(fill="x", pady=5)
        
        # Eco-Checkbox
        self.eco_cb = tk.Checkbutton(frame, text="Eco-Modus (RAM-sparend)", 
                                    variable=self.use_eco_mode,
                                    font=("Segoe UI", 10))
        self.eco_cb.pack(anchor="w")
        
        # Info-Text
        info_text = "Lädt PDF seitenweise statt auf einmal. Langsamer, aber stabil auf PCs mit wenig RAM."
        tk.Label(frame, text=info_text, font=("Segoe UI", 8), fg="#666",
                wraplength=550, justify="left").pack(anchor="w", pady=(5, 0))
    
    def _create_log_section(self, parent):
        frame = tk.LabelFrame(parent, text="Status", font=("Segoe UI", 9, "bold"))
        frame.pack(fill="both", expand=True, pady=5)
        
        self.log_text = tk.Text(frame, height=6, wrap="word", font=("Consolas", 9),
                               state="disabled", bg="#f8f9fa")
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)
    
    def _create_progress_section(self, parent):
        self.progress_bar = ttk.Progressbar(parent, variable=self.progress, 
                                           maximum=100, length=600)
        self.progress_bar.pack(fill="x", pady=10)
        
        tk.Label(parent, textvariable=self.status, font=("Segoe UI", 10, "bold"),
                fg="#0078d4").pack()
    
    def _create_buttons(self, parent):
        frame = tk.Frame(parent)
        frame.pack(fill="x", pady=10)
        
        self.btn_analyze = tk.Button(frame, text="📊 Analysieren", command=self.analyze,
                                    font=("Segoe UI", 11), width=18)
        self.btn_analyze.pack(side="left", padx=5)
        
        self.btn_preview = tk.Button(frame, text="👁 Vorschau", command=self.show_preview,
                                    font=("Segoe UI", 11), width=18)
        self.btn_preview.pack(side="left", padx=5)
        
        self.btn_convert = tk.Button(frame, text="🎵 Konvertieren", command=self.toggle_convert,
                                    bg="#107c10", fg="white", font=("Segoe UI", 11, "bold"),
                                    width=20, state="disabled")
        self.btn_convert.pack(side="right", padx=5)
    
    def _show_ram_warning(self):
        messagebox.showinfo("Eco-Modus empfohlen",
            f"Dein PC hat {self.ram_gb:.1f} GB RAM.\n\n"
            "Der Eco-Modus wurde automatisch aktiviert. "
            "Das macht die Konvertierung langsamer, aber stabiler.\n\n"
            "Bei kleinen PDFs (< 50 Seiten) kannst du den Eco-Modus ausprobieren.")
    
    def log(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")
    
    def browse_pdf(self):
        filename = filedialog.askopenfilename(title="PDF auswählen",
                                             filetypes=[("PDF", "*.pdf")])
        if filename:
            self.pdf_path.set(filename)
            self.output_path.set(str(Path(filename).with_suffix('.mp3')))
            self.btn_convert.config(state="normal")
            self.log(f"PDF gewählt: {Path(filename).name}")
    
    def browse_output(self):
        filename = filedialog.asksaveasfilename(title="Speichern unter",
                                               defaultextension=".mp3",
                                               filetypes=[("MP3", "*.mp3")])
        if filename:
            self.output_path.set(filename)
    
    def _map_rate(self, ui_value: str) -> str:
        mapping = {
            "sehr langsam": "-20%",
            "langsam": "-10%",
            "normal": "default",
            "schnell": "+10%",
            "sehr schnell": "+20%",
        }
        return mapping.get(ui_value, "default")
    
    def _map_pitch(self, ui_value: str) -> str:
        mapping = {
            "tief": "-10%",
            "normal": "default",
            "hoch": "+10%",
        }
        return mapping.get(ui_value, "default")
    
    def _map_volume(self, ui_value: str) -> str:
        mapping = {
            "leise": "soft",
            "normal": "default",
            "laut": "loud",
        }
        return mapping.get(ui_value, "default")
    
    def _map_url_mode(self, ui_value: str) -> str:
        mapping = {
            "Domain anzeigen": "domain",
            "Nur 'Link' sagen": "generic",
            "Entfernen": "remove",
            "Original lassen": "keep",
        }
        return mapping.get(ui_value, "domain")
    
    def _apply_preset(self, name: str, settings: dict):
        """Hilfsmethode zum Anwenden von Presets"""
        self.speaking_rate.set(settings.get('rate', 'normal'))
        self.pitch.set(settings.get('pitch', 'normal'))
        self.volume.set(settings.get('volume', 'normal'))
        self.url_mode.set(settings.get('url_mode', 'Domain anzeigen'))
        self.clean_lists.set(settings.get('clean_lists', True))
        self.fix_quotes.set(settings.get('fix_quotes', True))
        self.fix_thousands.set(settings.get('fix_thousands', True))
        self.remove_headers.set(settings.get('remove_headers', True))
        self.include_footnotes.set(settings.get('include_footnotes', False))
        self.use_ssml.set(settings.get('use_ssml', False))
        self.chunk_size.set(settings.get('chunk_size', 4000))
        self.log(f"Preset angewendet: {name}")
    
    def apply_adhd_preset(self):
        self._apply_preset("ADHD-Modus", {
            'rate': 'schnell',
            'url_mode': 'Entfernen',
        })
    
    def apply_academic_preset(self):
        self._apply_preset("Akademisch", {
            'url_mode': 'Domain anzeigen',
            'include_footnotes': True,
            'chunk_size': 3000,
        })
    
    def apply_fast_preset(self):
        self._apply_preset("Schnell", {
            'rate': 'sehr schnell',
            'url_mode': 'Entfernen',
        })
    
    def apply_slow_preset(self):
        self._apply_preset("Langsam", {
            'rate': 'sehr langsam',
            'url_mode': 'Domain anzeigen',
        })
    
    def analyze(self):
        if not self.pdf_path.get():
            messagebox.showwarning("Hinweis", "Bitte zuerst eine PDF wählen!")
            return
        
        self.status.set("Analysiere...")
        try:
            doc = fitz.open(self.pdf_path.get())
            pages = len(doc)
            
            # Sample Text
            sample = ""
            for i in range(min(3, pages)):
                sample += doc[i].get_text()
            
            words = len(sample.split())
            est_words = int(words / min(3, pages) * pages)
            duration = est_words // 130
            
            doc.close()
            
            self.log(f"Analyse: {pages} Seiten, ~{est_words} Wörter, ~{duration} Minuten")
            self.status.set("Analyse abgeschlossen")
            messagebox.showinfo("PDF Analyse", 
                f"Seiten: {pages}\nGeschätzte Dauer: ~{duration} Minuten")
        except Exception as e:
            messagebox.showerror("Fehler", str(e))
    
    def show_preview(self):
        if not self.pdf_path.get():
            messagebox.showwarning("Hinweis", "Bitte zuerst eine PDF wählen!")
            return
        
        self.status.set("Erstelle Vorschau...")
        try:
            parser = PDFIntelligentParser(self.pdf_path.get())
            try:
                text = parser.extract_text(
                    include_headers=not self.remove_headers.get(),
                    include_footnotes=self.include_footnotes.get(),
                    include_titles=True
                )
            finally:
                parser.close()
            
            cleaner = TextCleaner()
            cleaned = cleaner.clean(
                text,
                clean_lists=self.clean_lists.get(),
                url_mode=self._map_url_mode(self.url_mode.get()),
                fix_quotes=self.fix_quotes.get(),
                fix_thousands=self.fix_thousands.get()
            )
            
            # Nur die ersten ~3000 Zeichen für die Vorschau
            preview_text = cleaned[:3000]
            if len(cleaned) > 3000:
                preview_text += "\n\n[... Vorschau gekürzt ...]"
            
            # Vorschau-Fenster
            preview_window = tk.Toplevel(self.root)
            preview_window.title("Text-Vorschau")
            preview_window.geometry("700x500")
            preview_window.minsize(500, 400)
            
            tk.Label(preview_window, text="👁 Bereinigte Text-Vorschau (erste Zeilen)",
                    font=("Segoe UI", 12, "bold"), fg="#0078d4").pack(pady=10)
            
            text_widget = tk.Text(preview_window, wrap="word", font=("Consolas", 10),
                                 padx=10, pady=10)
            text_widget.pack(fill="both", expand=True, padx=10, pady=(0, 10))
            text_widget.insert("1.0", preview_text)
            text_widget.config(state="disabled")
            
            # Scrollbar
            scrollbar = ttk.Scrollbar(text_widget, command=text_widget.yview)
            text_widget.config(yscrollcommand=scrollbar.set)
            scrollbar.pack(side="right", fill="y")
            
            self.status.set("Vorschau bereit")
            self.log("Vorschau erstellt")
        except Exception as e:
            messagebox.showerror("Fehler", str(e))
            self.status.set("Fehler bei Vorschau")
    
    def toggle_convert(self):
        if self.is_converting:
            self.cancel_requested.set()
            self.status.set("⛔ Wird abgebrochen...")
            self.log("Abbruch angefordert...")
            return
        
        if not self.pdf_path.get():
            return
        
        self.is_converting = True
        self.cancel_requested.clear()
        self.btn_convert.config(text="⛔ Abbrechen", bg="#d32f2f")
        self.btn_analyze.config(state="disabled")
        self.btn_preview.config(state="disabled")
        
        thread = threading.Thread(target=self.convert)
        thread.daemon = True
        thread.start()
    
    def convert(self):
        try:
            eco = self.use_eco_mode.get()
            mode_text = "Eco-Modus" if eco else "Normal"
            self.log(f"Starte Konvertierung ({mode_text})...")
            
            engine = SmartTTSEngine(
                voice=self.selected_voice.get(),
                eco_mode=eco,
                speaking_rate=self._map_rate(self.speaking_rate.get()),
                pitch=self._map_pitch(self.pitch.get()),
                volume=self._map_volume(self.volume.get()),
                url_mode=self._map_url_mode(self.url_mode.get()),
                clean_lists=self.clean_lists.get(),
                fix_quotes=self.fix_quotes.get(),
                fix_thousands=self.fix_thousands.get(),
                include_headers=not self.remove_headers.get(),
                include_footnotes=self.include_footnotes.get(),
                use_ssml=self.use_ssml.get(),
                chunk_size=self.chunk_size.get(),
                cancel_event=self.cancel_requested
            )
            
            success = asyncio.run(engine.convert(
                self.pdf_path.get(),
                self.output_path.get(),
                progress_cb=self.update_progress
            ))
            
            engine.cleanup()
            
            if success:
                self.status.set("✅ Fertig!")
                self.progress.set(100)
                size = Path(self.output_path.get()).stat().st_size / (1024*1024)
                self.log(f"Fertig! Größe: {size:.1f} MB")
                messagebox.showinfo("Erfolg", f"MP3 erstellt!\n{self.output_path.get()}")
            else:
                raise Exception("Konvertierung fehlgeschlagen")
                
        except InterruptedError:
            self.log("Konvertierung vom Benutzer abgebrochen.")
            self.status.set("⛔ Abgebrochen")
        except Exception as e:
            self.log(f"Fehler: {e}")
            messagebox.showerror("Fehler", str(e))
        finally:
            self.is_converting = False
            self.root.after(0, self.reset_ui)
    
    def update_progress(self, message, percent):
        self.status.set(message)
        self.progress.set(percent)
        self.log(message)
    
    def reset_ui(self):
        self.btn_convert.config(state="normal", text="🎵 Konvertieren", bg="#107c10")
        self.btn_analyze.config(state="normal")
        self.btn_preview.config(state="normal")


def main():
    root = tk.Tk()
    app = SeraphinaSmartGUI(root)
    root.mainloop()


if __name__ == "__main__":
    import fitz  # Für __main__ test
    main()
