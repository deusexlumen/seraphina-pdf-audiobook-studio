#!/usr/bin/env python3
"""
Seraphina Simple GUI - Einfache tkinter Oberflaeche
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import asyncio
import tempfile
from pathlib import Path
import os
import sys

from voices import VOICES

# Unicode fix fuer Windows
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Imports
try:
    import edge_tts
    import fitz
except ImportError:
    messagebox.showerror("Fehler", "Bitte installiere zuerst:\npip install edge-tts PyMuPDF")
    sys.exit(1)


class SeraphinaGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Seraphina PDF zu MP3")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # Farben
        self.bg_color = "#f0f0f0"
        self.accent_color = "#0078d4"
        self.root.configure(bg=self.bg_color)
        
        # Variablen
        self.pdf_path = tk.StringVar()
        self.output_path = tk.StringVar(value=str(Path.home() / "Documents"))
        self.voice = tk.StringVar(value="Seraphina")
        self.status = tk.StringVar(value="Bereit")
        self.progress = tk.DoubleVar(value=0)
        
        self.is_converting = False
        
        self.build_ui()
    
    def build_ui(self):
        # Hauptframe
        main = tk.Frame(self.root, bg=self.bg_color, padx=20, pady=20)
        main.pack(fill="both", expand=True)
        
        # Titel
        tk.Label(main, text="Seraphina PDF zu MP3", 
                font=("Segoe UI", 18, "bold"),
                bg=self.bg_color, fg=self.accent_color).pack(pady=(0, 20))
        
        # PDF Auswahl
        frame1 = tk.LabelFrame(main, text="PDF Datei", bg=self.bg_color, 
                              font=("Segoe UI", 9, "bold"), padx=10, pady=10)
        frame1.pack(fill="x", pady=5)
        
        row1 = tk.Frame(frame1, bg=self.bg_color)
        row1.pack(fill="x")
        
        self.entry_pdf = tk.Entry(row1, textvariable=self.pdf_path, 
                                 font=("Segoe UI", 9), width=50)
        self.entry_pdf.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        tk.Button(row1, text="Durchsuchen", command=self.browse_pdf,
                 bg=self.accent_color, fg="white", cursor="hand2",
                 font=("Segoe UI", 9)).pack(side="right")
        
        # Einstellungen
        frame2 = tk.LabelFrame(main, text="Einstellungen", bg=self.bg_color,
                              font=("Segoe UI", 9, "bold"), padx=10, pady=10)
        frame2.pack(fill="x", pady=5)
        
        # Stimme
        tk.Label(frame2, text="Stimme:", bg=self.bg_color,
                font=("Segoe UI", 9)).grid(row=0, column=0, sticky="w", pady=5)
        
        ttk.Combobox(frame2, textvariable=self.voice, values=list(VOICES.keys()),
                    state="readonly", width=30).grid(row=0, column=1, sticky="w", padx=5)
        
        # Output
        tk.Label(frame2, text="Speichern unter:", bg=self.bg_color,
                font=("Segoe UI", 9)).grid(row=1, column=0, sticky="w", pady=5)
        
        row2 = tk.Frame(frame2, bg=self.bg_color)
        row2.grid(row=1, column=1, sticky="we", padx=5)
        
        tk.Entry(row2, textvariable=self.output_path,
                font=("Segoe UI", 9), width=40).pack(side="left", fill="x", expand=True)
        
        tk.Button(row2, text="Ändern", command=self.browse_output,
                 bg=self.accent_color, fg="white", cursor="hand2").pack(side="right", padx=(5, 0))
        
        # Info-Text
        self.info_text = tk.Text(main, height=6, width=70, wrap="word",
                                font=("Consolas", 9), state="disabled",
                                bg="white", fg="#333")
        self.info_text.pack(fill="x", pady=10)
        
        # Fortschritt
        self.progress_bar = ttk.Progressbar(main, variable=self.progress, 
                                           maximum=100, mode='determinate',
                                           length=560)
        self.progress_bar.pack(fill="x", pady=5)
        
        self.label_status = tk.Label(main, textvariable=self.status,
                                    bg=self.bg_color, font=("Segoe UI", 9, "bold"),
                                    fg="#666")
        self.label_status.pack(pady=5)
        
        # Buttons
        frame_buttons = tk.Frame(main, bg=self.bg_color)
        frame_buttons.pack(fill="x", pady=10)
        
        self.btn_analyze = tk.Button(frame_buttons, text="📊 PDF Analysieren",
                                    command=self.analyze, bg="#f0f0f0",
                                    font=("Segoe UI", 10), width=20)
        self.btn_analyze.pack(side="left", padx=5)
        
        self.btn_convert = tk.Button(frame_buttons, text="🎵 Zu MP3 Konvertieren",
                                    command=self.start_conversion,
                                    bg="#107c10", fg="white",
                                    font=("Segoe UI", 10, "bold"), width=25,
                                    cursor="hand2", state="disabled")
        self.btn_convert.pack(side="right", padx=5)
        
        # Initial log
        self.log("Willkommen! Wähle eine PDF-Datei und klicke auf 'Analysieren'.")
    
    def log(self, message):
        self.info_text.config(state="normal")
        self.info_text.insert("end", message + "\n")
        self.info_text.see("end")
        self.info_text.config(state="disabled")
        self.root.update()
    
    def browse_pdf(self):
        filename = filedialog.askopenfilename(
            title="PDF auswählen",
            filetypes=[("PDF Dateien", "*.pdf"), ("Alle Dateien", "*.*")]
        )
        if filename:
            self.pdf_path.set(filename)
            # Auto-output
            output = Path(filename).with_suffix('.mp3')
            self.output_path.set(str(output))
            self.btn_convert.config(state="normal")
            self.log(f"PDF ausgewählt: {Path(filename).name}")
    
    def browse_output(self):
        filename = filedialog.asksaveasfilename(
            title="Speichern unter",
            defaultextension=".mp3",
            filetypes=[("MP3 Dateien", "*.mp3")]
        )
        if filename:
            self.output_path.set(filename)
    
    def analyze(self):
        if not self.pdf_path.get():
            messagebox.showwarning("Hinweis", "Bitte zuerst eine PDF auswählen!")
            return
        
        self.status.set("Analysiere PDF...")
        self.progress.set(10)
        self.log("Analysiere PDF...")
        
        try:
            doc = fitz.open(self.pdf_path.get())
            pages = len(doc)
            
            # Sample erste Seite fuer Wortzahl-Schaetzung
            text_sample = ""
            for i in range(min(3, pages)):
                text_sample += doc[i].get_text()
            
            words_per_page = len(text_sample.split()) / min(3, pages) if text_sample else 200
            total_words = int(words_per_page * pages)
            duration_min = total_words // 130  # ca. 130 WPM
            
            doc.close()
            
            self.log(f"Ergebnis:")
            self.log(f"  Seiten: {pages}")
            self.log(f"  Geschätzte Wörter: {total_words}")
            self.log(f"  Geschätzte Dauer: ~{duration_min} Minuten")
            self.log(f"  Stimme: {self.voice.get()}")
            
            self.status.set("Analyse abgeschlossen")
            self.progress.set(0)
            self.btn_convert.config(state="normal")
            
        except Exception as e:
            messagebox.showerror("Fehler", str(e))
            self.status.set("Fehler bei Analyse")
    
    def start_conversion(self):
        if self.is_converting:
            return
        
        if not self.pdf_path.get():
            messagebox.showwarning("Hinweis", "Bitte eine PDF auswählen!")
            return
        
        self.is_converting = True
        self.btn_convert.config(state="disabled", text="Konvertiere...")
        self.btn_analyze.config(state="disabled")
        
        # Starte in Thread
        thread = threading.Thread(target=self.convert)
        thread.daemon = True
        thread.start()
    
    def convert(self):
        try:
            self.status.set("Lese PDF...")
            self.progress.set(5)
            
            # PDF zu Text - seitenweise fuer RAM-Ersparnis
            doc = fitz.open(self.pdf_path.get())
            total_pages = len(doc)
            
            # Temp Verzeichnis
            temp_dir = Path(tempfile.mkdtemp())
            chunk_files = []
            
            from text_cleaner import TextCleaner
            cleaner = TextCleaner()
            voice_id = VOICES.get(self.voice.get(), VOICES['Seraphina'])
            output_file = self.output_path.get()
            
            for i in range(total_pages):
                self.progress.set(5 + (i / total_pages) * 20)
                self.status.set(f"Lese Seite {i+1}/{total_pages}...")
                self.root.update()
                
                page = doc[i]
                raw_text = page.get_text()
                
                if len(raw_text.strip()) < 10:
                    continue
                
                # Text bereinigen fuer fluessiges Vorlesen
                clean = cleaner.clean(raw_text)
                if len(clean) < 20:
                    continue
                
                chunk_file = temp_dir / f"page_{i:04d}.mp3"
                
                try:
                    communicate = edge_tts.Communicate(clean, voice_id)
                    asyncio.run(communicate.save(str(chunk_file)))
                    chunk_files.append(chunk_file)
                except Exception as e:
                    self.log(f"Fehler bei Seite {i+1}: {e}")
            
            doc.close()
            
            if not chunk_files:
                raise Exception("Zu wenig Text gefunden!")
            
            self.log(f"Text bereinigt und {len(chunk_files)} Audio-Seiten generiert.")
            
            # Kombiniere
            self.status.set("Kombiniere Audio...")
            self.progress.set(30)
            self.combine_chunks(chunk_files, output_file, temp_dir)
            
            # Cleanup
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            if os.path.exists(output_file):
                size_mb = os.path.getsize(output_file) / (1024 * 1024)
                self.log(f"✓ Fertig! Gespeichert: {output_file}")
                self.log(f"  Größe: {size_mb:.2f} MB")
                self.status.set("Fertig!")
                self.progress.set(100)
                messagebox.showinfo("Erfolg", f"MP3 erstellt!\n\n{output_file}")
            else:
                raise Exception("Ausgabedatei nicht gefunden")
                
        except Exception as e:
            self.log(f"FEHLER: {str(e)}")
            self.status.set("Fehler!")
            messagebox.showerror("Fehler", str(e))
        
        finally:
            self.is_converting = False
            self.root.after(0, self.reset_ui)
    
    def combine_chunks(self, chunk_files, output_file, temp_dir):
        """Kombiniert Chunks mit ffmpeg oder Python-only"""
        self.status.set("Kombiniere Audio...")
        
        # Concat-Liste
        list_file = temp_dir / "list.txt"
        with open(list_file, 'w') as f:
            for cf in chunk_files:
                f.write(f"file '{cf.name}'\n")
        
        # FFmpeg
        import subprocess
        try:
            cmd = [
                'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
                '-i', str(list_file), '-c', 'copy', output_file
            ]
            subprocess.run(cmd, cwd=temp_dir, capture_output=True, check=True)
            return
        except Exception:
            pass
        
        # Python-only Fallback: Dateien binaer anhaengen
        try:
            with open(output_file, 'wb') as outfile:
                for cf in chunk_files:
                    with open(cf, 'rb') as infile:
                        outfile.write(infile.read())
            return
        except Exception:
            pass
        
        # Letzter Fallback: erster Chunk
        import shutil
        shutil.copy(chunk_files[0], output_file)
    
    def reset_ui(self):
        self.btn_convert.config(state="normal", text="🎵 Zu MP3 Konvertieren")
        self.btn_analyze.config(state="normal")
        self.progress.set(0)


def main():
    root = tk.Tk()
    app = SeraphinaGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
