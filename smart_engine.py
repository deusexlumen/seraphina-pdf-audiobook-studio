#!/usr/bin/env python3
"""
Seraphina Smart Engine - Eine Engine, zwei Modi
Auto-Detection für RAM oder manuelle Auswahl
"""

import asyncio
import edge_tts
import fitz
import os
import re
import tempfile
import shutil
import subprocess
import gc
from pathlib import Path
from typing import List, Optional, Callable
import threading

from pdf_parser import PDFIntelligentParser
from text_cleaner import TextCleaner
from ssml_generator import IntelligentSSMLGenerator
from voices import VOICES


class SmartTTSEngine:
    """
    Intelligente TTS-Engine mit zwei Modi:
    - Normal: Alles auf einmal (schnell, braucht RAM)
    - Eco: Seitenweise (langsam, spart RAM)
    """
    
    def __init__(self, voice: str = 'Seraphina', eco_mode: bool = False,
                 speaking_rate: str = "default", pitch: str = "default",
                 volume: str = "default", url_mode: str = "domain",
                 clean_lists: bool = True, fix_quotes: bool = True,
                 fix_thousands: bool = True, include_headers: bool = False,
                 include_footnotes: bool = False, use_ssml: bool = False,
                 chunk_size: int = 4000,
                 cancel_event: Optional[threading.Event] = None):
        self.voice_name = VOICES.get(voice, VOICES['Seraphina'])
        self.eco_mode = eco_mode
        self.speaking_rate = speaking_rate
        self.pitch = pitch
        self.volume = volume
        self.url_mode = url_mode
        self.clean_lists = clean_lists
        self.fix_quotes = fix_quotes
        self.fix_thousands = fix_thousands
        self.include_headers = include_headers
        self.include_footnotes = include_footnotes
        self.use_ssml = use_ssml
        self.chunk_size = chunk_size
        self.cancelled = cancel_event if cancel_event is not None else threading.Event()
        
        self.temp_dir = Path(tempfile.mkdtemp())
        self.progress_callback: Optional[Callable] = None
        self.text_cleaner = TextCleaner()
    
    def _check_cancelled(self):
        """Prueft ob die Konvertierung abgebrochen wurde"""
        if self.cancelled.is_set():
            raise InterruptedError("Konvertierung abgebrochen")
    
    @staticmethod
    def detect_ram() -> float:
        """Erkennt verfügbaren RAM in GB"""
        try:
            import psutil
            return psutil.virtual_memory().total / (1024**3)
        except:
            return 8.0  # Default wenn nicht erkannt
    
    @staticmethod
    def should_use_eco_mode() -> bool:
        """Empfiehlt Eco-Mode basierend auf RAM"""
        ram = SmartTTSEngine.detect_ram()
        return ram < 6.0  # Unter 6GB = Eco empfohlen
    
    def extract_text(self, pdf_path: str, progress_cb: Optional[Callable] = None) -> str:
        """Extrahiert Text aus PDF mit intelligentem Parser und Bereinigung"""
        parser = PDFIntelligentParser(pdf_path)
        
        try:
            text = parser.extract_text(
                include_headers=self.include_headers,
                include_footnotes=self.include_footnotes,
                include_titles=True
            )
        finally:
            parser.close()
        
        # Text bereinigen
        return self.text_cleaner.clean(
            text,
            clean_lists=self.clean_lists,
            url_mode=self.url_mode,
            fix_quotes=self.fix_quotes,
            fix_thousands=self.fix_thousands
        )
    
    def _clean_text(self, text: str) -> str:
        """Bereinigt Text für flüssiges Vorlesen (Legacy, wird durch TextCleaner ersetzt)"""
        return self.text_cleaner.clean(
            text,
            clean_lists=self.clean_lists,
            url_mode=self.url_mode,
            fix_quotes=self.fix_quotes,
            fix_thousands=self.fix_thousands
        )
    
    def _apply_ssml(self, text: str) -> str:
        """Wendet optional SSML auf den Text an"""
        if not self.use_ssml:
            return text
        
        generator = IntelligentSSMLGenerator(
            voice_name=self.voice_name,
            speaking_rate=self.speaking_rate,
            pitch=self.pitch,
            volume=self.volume
        )
        optimized = generator.optimize_for_reading(text)
        return generator.text_to_ssml(optimized)
    
    async def convert(self, pdf_path: str, output_path: str, 
                     progress_cb: Optional[Callable] = None) -> bool:
        """
        Hauptkonvertierungsmethode
        Wählt automatisch zwischen Normal und Eco-Modus
        """
        self.progress_callback = progress_cb
        
        if self.eco_mode:
            return await self._convert_eco(pdf_path, output_path)
        else:
            return await self._convert_normal(pdf_path, output_path)
    
    async def _convert_normal(self, pdf_path: str, output_path: str) -> bool:
        """Normal-Modus: Alles auf einmal"""
        self._check_cancelled()
        
        # Text extrahieren
        text = self.extract_text(pdf_path, self.progress_callback)
        
        if not text or len(text) < 50:
            raise ValueError("Zu wenig Text gefunden")
        
        # Optional SSML anwenden
        text = self._apply_ssml(text)
        
        # In Chunks aufteilen
        chunks = self._split_text(text, self.chunk_size)
        
        # Audio generieren
        return await self._generate_audio_chunks(chunks, output_path)
    
    async def _convert_eco(self, pdf_path: str, output_path: str) -> bool:
        """Eco-Modus: Seitenweise mit Speicher-Freigabe"""
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        chunk_files = []
        
        try:
            for page_num in range(total_pages):
                if self.progress_callback:
                    progress = (page_num / total_pages) * 100
                    self.progress_callback(f"Verarbeite Seite {page_num+1}/{total_pages}", progress)
                
                # Nur diese Seite laden
                page = doc[page_num]
                text = page.get_text()
                
                if not text.strip():
                    continue
                
                # Bereinigen
                clean = self.text_cleaner.clean(
                    text,
                    clean_lists=self.clean_lists,
                    url_mode=self.url_mode,
                    fix_quotes=self.fix_quotes,
                    fix_thousands=self.fix_thousands
                )
                if len(clean) < 20:
                    continue
                
                # SSML wird im Eco-Modus nicht pro Seite angewendet,
                # um geschachtelte <speak>-Tags zu vermeiden
                
                # Audio für diese Seite generieren
                chunk_file = self.temp_dir / f"page_{page_num:04d}.mp3"
                await self._generate_chunk(clean, str(chunk_file))
                chunk_files.append(chunk_file)
                
                # SPEICHER FREIGEBEN (wichtig für 4GB!)
                gc.collect()
        finally:
            doc.close()
        
        # Kombinieren
        return self._combine_chunks(chunk_files, output_path)
    
    def _split_text(self, text: str, max_length: int) -> List[str]:
        """Teilt Text intelligent an Satzgrenzen in Chunks"""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current = ""
        
        for sentence in sentences:
            if len(current) + len(sentence) < max_length:
                current += " " + sentence if current else sentence
            else:
                if current:
                    chunks.append(current.strip())
                current = sentence
        
        if current:
            chunks.append(current.strip())
        
        return chunks if chunks else [text]
    
    async def _generate_audio_chunks(self, chunks: List[str], output_path: str) -> bool:
        """Generiert Audio für alle Chunks"""
        chunk_files = []
        total = len(chunks)
        
        for i, chunk in enumerate(chunks, 1):
            if self.progress_callback:
                progress = 30 + (i / total) * 60
                self.progress_callback(f"Generiere Audio {i}/{total}", progress)
            
            chunk_file = self.temp_dir / f"chunk_{i:04d}.mp3"
            await self._generate_chunk(chunk, str(chunk_file))
            chunk_files.append(chunk_file)
        
        return self._combine_chunks(chunk_files, output_path)
    
    async def _generate_chunk(self, text: str, output_file: str):
        """Generiert einzelnen Audio-Chunk"""
        communicate = edge_tts.Communicate(text, self.voice_name)
        await communicate.save(output_file)
    
    def _combine_chunks(self, chunk_files: List[Path], output_path: str) -> bool:
        """Kombiniert Chunks zu einer MP3"""
        if not chunk_files:
            return False
        
        if len(chunk_files) == 1:
            shutil.copy(chunk_files[0], output_path)
            return True
        
        # 1. Versuche ffmpeg
        try:
            list_file = self.temp_dir / "concat.txt"
            with open(list_file, 'w') as f:
                for cf in chunk_files:
                    f.write(f"file '{cf.name}'\n")
            
            cmd = [
                'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
                '-i', str(list_file), '-c', 'copy', output_path
            ]
            result = subprocess.run(cmd, cwd=self.temp_dir, capture_output=True)
            
            if result.returncode == 0 and Path(output_path).exists() and Path(output_path).stat().st_size > 0:
                return True
        except Exception:
            pass
        
        # 2. Python-only Fallback: Dateien binaer anhaengen
        try:
            with open(output_path, 'wb') as outfile:
                for cf in chunk_files:
                    with open(cf, 'rb') as infile:
                        outfile.write(infile.read())
            return True
        except Exception:
            pass
        
        # 3. Letzter Fallback: erster Chunk
        shutil.copy(chunk_files[0], output_path)
        return True
    
    def cleanup(self):
        """Räumt temporäre Dateien auf"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)


if __name__ == "__main__":
    # Test
    engine = SmartTTSEngine()
    ram = engine.detect_ram()
    eco = engine.should_use_eco_mode()
    print(f"RAM: {ram:.1f} GB")
    print(f"Eco-Mode empfohlen: {eco}")
