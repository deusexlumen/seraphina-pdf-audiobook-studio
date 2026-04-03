#!/usr/bin/env python3
"""
Seraphina ULTRA-LIGHT - Für alte/schwache PCs (2-4GB RAM)
- Keine GUI (spart RAM)
- Keine async (spart Overhead)  
- Speichert jede Seite SOFORT (nics im RAM halten)
- Kein FFmpeg nötig (reines Python)
"""

import sys
import os
import gc
from pathlib import Path

# SPEICHER SPAREN: Keine unnötigen Imports
def ultra_light_convert():
    print("=" * 50)
    print("  SERAPHINA ULTRA-LIGHT")
    print("  Für sehr schwache PCs (2-4GB RAM)")
    print("=" * 50)
    
    # Nur nötige Imports hier (spart RAM beim Start)
    print("\nLade Module...")
    try:
        import edge_tts
        import fitz
        import asyncio
        from text_cleaner import TextCleaner
        from voices import VOICES
    except ImportError as e:
        print(f"\n❌ Fehlendes Modul: {e}")
        print("Installiere: pip install edge-tts PyMuPDF")
        input("Enter...")
        return
    
    # PDF wählen
    print("\nPDF-Dateien:")
    pdfs = list(Path('.').glob('*.pdf'))
    
    if not pdfs:
        path = input("PDF-Pfad: ").strip('"')
    else:
        for i, pdf in enumerate(pdfs, 1):
            size = pdf.stat().st_size / 1024
            print(f"  [{i}] {pdf.name} ({size:.0f} KB)")
        
        choice = input("\nWähle [1-{}]: ".format(len(pdfs))).strip()
        try:
            path = str(pdfs[int(choice)-1])
        except:
            path = str(pdfs[0]) if pdfs else ""
    
    if not path or not os.path.exists(path):
        print("❌ Nicht gefunden!")
        return
    
    # Output
    output = Path(path).with_suffix('.mp3')
    print(f"\nOutput: {output.name}")
    
    # Stimme
    voice_names = list(VOICES.keys())[:3]
    for idx, name in enumerate(voice_names, 1):
        print(f"[{idx}] {name}")
    voice_choice = input(f"Stimme [1-{len(voice_names)}]: ").strip() or "1"
    
    try:
        voice = VOICES[voice_names[int(voice_choice) - 1]]
    except (ValueError, IndexError):
        voice = VOICES[voice_names[0]]
    
    confirm = input("\nStarten? [j]: ").lower()
    if confirm and confirm != 'j':
        return
    
    # WICHTIG: Temp-Ordner für einzelne Seiten
    temp_dir = Path("temp_ultra")
    temp_dir.mkdir(exist_ok=True)
    
    try:
        # PDF öffnen
        print("\nÖffne PDF...")
        doc = fitz.open(path)
        total = len(doc)
        
        print(f"Seiten: {total}")
        print("\nVerarbeite seitenweise (Ultra-Spar-Modus)...")
        print("(Jede Seite wird sofort gespeichert, nichts im RAM)\n")
        
        page_files = []
        
        async def process_all_pages():
            """Ein async-Loop für alle Seiten"""
            for i in range(total):
                print(f"Seite {i+1}/{total}...", end=" ", flush=True)
                
                # NUR diese Seite laden
                page = doc.load_page(i)  # Lazy loading!
                text = page.get_text()
                
                # Sofort schließen (SPEICHER FREI!)
                page.clean_contents()
                del page
                
                # Text bereinigen (vollständig, aber seitenweise für RAM-Ersparnis)
                cleaner = TextCleaner()
                clean = cleaner.clean(text)
                
                if len(clean) < 10:
                    print("(leer)")
                    continue
                
                # SOFORT Audio generieren für diese Seite
                page_file = temp_dir / f"p{i:04d}.mp3"
                
                try:
                    communicate = edge_tts.Communicate(clean, voice)
                    await communicate.save(str(page_file))
                    page_files.append(page_file)
                    print("✓")
                except Exception as e:
                    print(f"✗ ({e})")
                
                # EXTREME SPEICHER-FREIGABE
                del text, clean
                gc.collect()  # FORCE garbage collection!
        
        # SEITE FÜR SEITE - nie alles auf einmal laden!
        asyncio.run(process_all_pages())
        
        doc.close()
        
        if not page_files:
            print("\n❌ Keine Audio-Dateien erstellt!")
            return
        
        # Kombinieren (ohne FFmpeg!)
        print(f"\n{len(page_files)} Seiten erstellt.")
        print("Kombiniere zu einer Datei...")
        
        # Python-only: Einfach Dateien anhängen
        with open(output, 'wb') as outfile:
            for i, pf in enumerate(page_files, 1):
                print(f"  {i}/{len(page_files)}...", end="\r")
                with open(pf, 'rb') as infile:
                    outfile.write(infile.read())
        
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)
        
        # Fertig
        size = output.stat().st_size / (1024*1024)
        print(f"\n✅ Fertig!")
        print(f"   {output}")
        print(f"   Größe: {size:.1f} MB")
        
    except Exception as e:
        print(f"\n❌ Fehler: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nEnter zum Beenden...")


if __name__ == "__main__":
    try:
        ultra_light_convert()
    except KeyboardInterrupt:
        print("\n\nAbgebrochen")
    except Exception as e:
        print(f"\n💥 Kritischer Fehler: {e}")
        input("Enter...")
