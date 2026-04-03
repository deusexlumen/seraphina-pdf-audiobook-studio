"""
SSML Generator - Erzeugt intelligente SSML-Tags
Erkennt: Fragen, Emotionen, Satzstruktur
"""

import re
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Sentence:
    """Repraesentiert einen Satz mit Metadaten"""
    text: str
    sentence_type: str = "statement"  # 'question', 'exclamation', 'ellipsis', 'normal'
    emotion: Optional[str] = None     # 'excited', 'angry', 'happy', 'sad', 'neutral'
    emphasis: bool = False
    

class IntelligentSSMLGenerator:
    """
    Generiert SSML-Tags basierend auf Textanalyse
    """
    
    # Emotions-Keywords fuer heuristische Erkennung
    EMOTION_KEYWORDS = {
        'excited': ['unglaublich', 'fantastisch', 'wunderbar', 'super', 'genial', 
                   'wow', 'toll', 'erstaunlich', 'unglaublich', 'perfekt'],
        'angry': ['wuetend', 'aergerlich', 'verdammt', 'furchtbar', 'schrecklich',
                 'hass', 'wut', 'aggressiv', 'empoert'],
        'happy': ['gluecklich', 'froehlich', 'freude', 'jubel', 'strahlen',
                 'begeistert', 'glücklich', 'zufrieden'],
        'sad': ['traurig', 'weinen', 'schmerz', 'leid', 'deprimiert',
               'enttaeuscht', 'melancholisch'],
        'fear': ['angst', 'furcht', 'panik', 'schockiert', 'erschrocken',
                'besorgt', 'nervoes']
    }
    
    def __init__(self, voice_name: str = "de-DE-SeraphinaMultilingualNeural",
                 speaking_rate: str = "default",
                 pitch: str = "default",
                 volume: str = "default"):
        self.voice_name = voice_name
        self.speaking_rate = speaking_rate
        self.pitch = pitch
        self.volume = volume
    
    def analyze_sentence(self, text: str) -> Sentence:
        """Analysiert einen Satz und bestimmt Typ und Emotion"""
        text = text.strip()
        
        if not text:
            return Sentence(text="", sentence_type="empty")
        
        sentence = Sentence(text=text)
        
        # 1. Satztyp erkennen
        if text.endswith('?'):
            sentence.sentence_type = "question"
        elif text.endswith('!'):
            sentence.sentence_type = "exclamation"
        elif text.endswith('...'):
            sentence.sentence_type = "ellipsis"
        
        # 2. Emotion erkennen (Keywords)
        text_lower = text.lower()
        for emotion, keywords in self.EMOTION_KEYWORDS.items():
            if any(keyword in text_lower for keyword in keywords):
                sentence.emotion = emotion
                break
        
        # 3. Emotion durch Satzzeichen bestaerken
        if sentence.sentence_type == "exclamation":
            if not sentence.emotion:
                sentence.emotion = "excited"
        
        # 4. GROSSBUCHSTABEN = Betonung
        if text.isupper():
            sentence.emphasis = True
        elif any(word.isupper() and len(word) > 2 for word in text.split()):
            sentence.emphasis = True
        
        return sentence
    
    def generate_ssml_for_sentence(self, sentence: Sentence) -> str:
        """Generiert SSML fuer einen einzelnen Satz"""
        text = sentence.text
        
        # Kein SSML fuer leere Saetze
        if not text:
            return ""
        
        # Basis-Attribute
        pitch = "default"
        rate = "default"
        volume = "default"
        
        # Fragen: Pitch hoch
        if sentence.sentence_type == "question":
            pitch = "+15%"
            rate = "medium"
        
        # Ausrufe: Pitch hoch, schneller
        elif sentence.sentence_type == "exclamation":
            if sentence.emotion == "angry":
                pitch = "-10%"
                rate = "slow"
                volume = "loud"
            elif sentence.emotion == "excited":
                pitch = "+20%"
                rate = "fast"
                volume = "loud"
            else:
                pitch = "+10%"
                rate = "medium"
        
        # Ellipsis (...): Pause, langsamer
        elif sentence.sentence_type == "ellipsis":
            rate = "slow"
            pitch = "-5%"
        
        # Emotionen
        if sentence.emotion == "happy":
            pitch = "+15%"
        elif sentence.emotion == "sad":
            pitch = "-15%"
            rate = "slow"
        elif sentence.emotion == "fear":
            pitch = "+10%"
            rate = "fast"
            volume = "soft"
        
        # Betonung
        if sentence.emphasis:
            volume = "loud"
        
        # Baue SSML
        attrs = []
        if pitch != "default":
            attrs.append(f'pitch="{pitch}"')
        if rate != "default":
            attrs.append(f'rate="{rate}"')
        if volume != "default":
            attrs.append(f'volume="{volume}"')
        
        if attrs:
            prosody_attr = " ".join(attrs)
            return f'<prosody {prosody_attr}>{text}</prosody>'
        else:
            return text
    
    def text_to_ssml(self, text: str, add_pauses: bool = True) -> str:
        """
        Konvertiert einen Textblock zu SSML
        
        Args:
            text: Der zu konvertierende Text
            add_pauses: Pausen nach Absaetzen einfuegen
        """
        # Teile in Saetze
        # Unterstuetzt: . ! ? ...
        sentences_raw = re.split(r'(?<=[.!?])\s+', text)
        
        # Filtere leere Saetze
        sentences_raw = [s.strip() for s in sentences_raw if s.strip()]
        
        # Analysiere und konvertiere jeden Satz
        ssml_parts = []
        
        for raw_sentence in sentences_raw:
            # Erkenne Absatz-Pausen ([PAUSE] Marker vom Parser)
            if "[PAUSE]" in raw_sentence:
                raw_sentence = raw_sentence.replace("[PAUSE]", "").strip()
                if not raw_sentence:
                    ssml_parts.append('<break time="1000ms"/>')
                    continue
            
            sentence = self.analyze_sentence(raw_sentence)
            ssml_part = self.generate_ssml_for_sentence(sentence)
            ssml_parts.append(ssml_part)
        
        # Verbinde mit Pausen zwischen Saetzen
        ssml_content = " ".join(ssml_parts)
        
        # Globale Prosody-Attribute anwenden
        global_attrs = []
        if self.speaking_rate != "default":
            global_attrs.append(f'rate="{self.speaking_rate}"')
        if self.pitch != "default":
            global_attrs.append(f'pitch="{self.pitch}"')
        if self.volume != "default":
            global_attrs.append(f'volume="{self.volume}"')
        
        if global_attrs:
            global_prosody = " ".join(global_attrs)
            ssml_content = f'<prosody {global_prosody}>{ssml_content}</prosody>'
        
        # Wrap in speak-Tag
        ssml = f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="de-DE">{ssml_content}</speak>'
        
        return ssml
    
    def optimize_for_reading(self, text: str) -> str:
        """
        Optimiert Text fuer Vorlesen:
        - Entfernt unnoetige Zeichen
        - Ersetzt Abkuerzungen
        - Bereinigt Formatierung
        """
        # Ersetze haeufige Abkuerzungen
        replacements = {
            r'\b(z\.\s*B\.|z\.B\.)\b': 'zum Beispiel',
            r'\b(u\.\s*a\.|u\.a\.)\b': 'unter anderem',
            r'\b(d\.\s*h\.|d\.h\.)\b': 'das heisst',
            r'\b(v\.\s*a\.|v\.a\.)\b': 'vor allem',
            r'\b(etc\.)\b': 'et cetera',
            r'\b(ca\.\s)': 'circa ',
            r'\b(ca\.)\b': 'circa',
            r'\b(Dr\.\s)': 'Doktor ',
            r'\b(Prof\.\s)': 'Professor ',
            r'\b(Mr\.\s)': 'Mister ',
            r'\b(Mrs\.\s)': 'Misses ',
            r'\s+': ' ',  # Mehrfache Leerzeichen
        }
        
        for pattern, replacement in replacements.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        # Entferne URLs (optional - kann auch ausgesprochen werden)
        # text = re.sub(r'https?://\S+', '', text)
        
        # Bereinige Zeilenumbrueche
        text = text.replace('\n\n', ' [PAUSE] ')
        text = text.replace('\n', ' ')
        
        return text.strip()


# Test
if __name__ == "__main__":
    generator = IntelligentSSMLGenerator(
        speaking_rate="+10%",
        pitch="default",
        volume="default"
    )
    
    test_texts = [
        "Hast du das verstanden? Das ist wichtig!",
        "Er war wirklich wuetend auf sie.",
        "Das ist einfach unglaublich! Fantastisch!",
        "Sie war so gluecklich und strahlte vor Freude.",
        "Er wartete... und wartete... aber nichts passierte.",
        "ACHTUNG! Das ist gefaehrlich!"
    ]
    
    print("SSML Generator Tests:\n")
    for text in test_texts:
        print(f"Input:  {text}")
        optimized = generator.optimize_for_reading(text)
        ssml = generator.text_to_ssml(optimized)
        print(f"SSML:   {ssml}\n")
