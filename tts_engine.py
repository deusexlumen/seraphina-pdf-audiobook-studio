"""
TTS Engine - Edge-TTS Integration mit Batch-Verarbeitung
"""

import asyncio
import edge_tts
import tempfile
import os
from pathlib import Path
from typing import Callable, Optional
import subprocess

from voices import VOICES


class EdgeTTSEngine:
    """
    Wrapper fuer edge-tts mit Fortschritts-Tracking
    """
    
    def __init__(self, voice: str = 'Seraphina', progress_callback: Optional[Callable] = None):
        self.voice_name = VOICES.get(voice, VOICES['Seraphina'])
        self.progress_callback = progress_callback
        self.temp_dir = tempfile.mkdtemp()
    
    async def _generate_chunk(self, text: str, output_file: str) -> bool:
        """Generiert einen Text-Chunk zu MP3"""
        try:
            communicate = edge_tts.Communicate(text, self.voice_name)
            await communicate.save(output_file)
            return True
        except Exception as e:
            print(f"Fehler bei Chunk-Generierung: {e}")
            return False
    
    def generate_audio(self, text: str, output_path: str, 
                      split_chunks: bool = True,
                      chunk_size: int = 5000) -> bool:
        """
        Generiert Audio aus Text
        
        Args:
            text: Der zu synthetisierende Text (plain oder SSML)
            output_path: Ziel-MP3-Datei
            split_chunks: Text in Chunks aufteilen (fuer lange Texte)
            chunk_size: Max. Zeichen pro Chunk
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if split_chunks and len(text) > chunk_size:
            return self._generate_long_text(text, output_path, chunk_size)
        else:
            # Einzelner Chunk
            temp_file = os.path.join(self.temp_dir, "temp_audio.mp3")
            success = asyncio.run(self._generate_chunk(text, temp_file))
            if success:
                os.rename(temp_file, str(output_path))
            return success
    
    def _generate_long_text(self, text: str, output_path: Path, chunk_size: int) -> bool:
        """
        Generiert lange Texte in Chunks und fuegt sie zusammen
        """
        # Teile Text an Satzgrenzen
        chunks = self._split_text_smart(text, chunk_size)
        total_chunks = len(chunks)
        
        print(f"Generiere {total_chunks} Chunks...")
        
        chunk_files = []
        for i, chunk in enumerate(chunks, 1):
            if self.progress_callback:
                self.progress_callback(i, total_chunks, f"Chunk {i}/{total_chunks}")
            
            chunk_file = os.path.join(self.temp_dir, f"chunk_{i:04d}.mp3")
            success = asyncio.run(self._generate_chunk(chunk, chunk_file))
            
            if success:
                chunk_files.append(chunk_file)
            else:
                print(f"Fehler bei Chunk {i}")
        
        if not chunk_files:
            return False
        
        # Fuege Chunks zusammen (mit ffmpeg)
        return self._concatenate_chunks(chunk_files, str(output_path))
    
    def _split_text_smart(self, text: str, max_length: int) -> list:
        """
        Teilt Text intelligent an Satzgrenzen
        """
        sentences = []
        # Einfache Satz-Erkennung
        import re
        raw_sentences = re.split(r'(?<=[.!?])\s+', text)
        
        current_chunk = ""
        for sentence in raw_sentences:
            if len(current_chunk) + len(sentence) < max_length:
                current_chunk += " " + sentence if current_chunk else sentence
            else:
                if current_chunk:
                    sentences.append(current_chunk.strip())
                current_chunk = sentence
        
        if current_chunk:
            sentences.append(current_chunk.strip())
        
        return sentences if sentences else [text]
    
    def _concatenate_chunks(self, chunk_files: list, output_file: str) -> bool:
        """
        Fuegt MP3-Chunks mit ffmpeg oder Python-only zusammen
        """
        try:
            # Erstelle Concat-Liste
            list_file = os.path.join(self.temp_dir, "concat_list.txt")
            with open(list_file, 'w', encoding='utf-8') as f:
                for chunk in chunk_files:
                    # Escaping fuer Windows-Pfade
                    escaped = chunk.replace('\\', '/')
                    f.write(f"file '{escaped}'\n")
            
            # ffmpeg concat
            cmd = [
                'ffmpeg',
                '-y',  # Ueberschreiben
                '-f', 'concat',
                '-safe', '0',
                '-i', list_file,
                '-acodec', 'copy',
                output_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return True
        except Exception as e:
            print(f"ffmpeg Fehler: {e}")
        
        # Python-only Fallback: Dateien binaer anhaengen
        try:
            with open(output_file, 'wb') as outfile:
                for chunk in chunk_files:
                    with open(chunk, 'rb') as infile:
                        outfile.write(infile.read())
            return True
        except Exception as e:
            print(f"Fehler beim Python-Fallback: {e}")
        
        # Letzter Fallback: Kopiere ersten Chunk
        if chunk_files:
            import shutil
            shutil.copy(chunk_files[0], output_file)
            return True
        return False
    
    def cleanup(self):
        """Raeumt temporaere Dateien auf"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @staticmethod
    def list_voices():
        """Zeigt verfuegbare Stimmen"""
        print("Verfuegbare Stimmen:")
        for name, voice_id in VOICES.items():
            print(f"  {name}: {voice_id}")


# Test
if __name__ == "__main__":
    engine = EdgeTTSEngine('Seraphina')
    
    # Test-Text
    test_text = "Hallo! Das ist ein Test der Seraphina Stimme. Sie funktioniert einwandfrei!"
    
    print("Generiere Test-Audio...")
    success = engine.generate_audio(
        test_text,
        "test_output.mp3",
        split_chunks=False
    )
    
    if success:
        print("✓ Test-Audio erstellt: test_output.mp3")
    else:
        print("✗ Fehler bei der Generierung")
    
    engine.cleanup()
