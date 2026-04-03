#!/usr/bin/env python3
"""
Text Cleaner - Entfernt störende PDF-Formatierung
Speziell für flüssiges Vorlesen optimiert (ADHS-freundlich)
"""

import re
from typing import List, Tuple


class TextCleaner:
    """
    Bereinigt PDF-Text für natürliches Vorlesen
    """
    
    def __init__(self):
        # Muster für Satzende
        self.sentence_endings = re.compile(r'[.!?]+')
        
        # Trennzeichen am Zeilenende (Bindestriche)
        self.hyphen_pattern = re.compile(r'(\w+)-\s*\n\s*(\w+)')
        
        # Ungültige Zeichen
        self.invalid_chars = re.compile(r'[^\w\s\.\,\!\?\;\:\-\(\)\"\'äöüÄÖÜß]')
        
        # Aufzählungsmuster
        self.bullet_pattern = re.compile(r'^[\s]*[•▪►●○■\-\*][\s]+', re.MULTILINE)
        self.letter_enum_pattern = re.compile(r'^[\s]*([a-fA-F])[\.\)][\s]+', re.MULTILINE)
        self.number_enum_pattern = re.compile(r'^[\s]*(\d+)[\.\)][\s]+', re.MULTILINE)
        
        # URL-Muster
        self.url_pattern = re.compile(r'https?://[^\s\)\]\>]+')
        self.www_pattern = re.compile(r'www\.[^\s\)\]\>]+')
        
        # Anführungszeichen
        self.german_quotes_open = re.compile(r'[„"»«]')
        self.german_quotes_close = re.compile(r'[\""»«]')
        
        # Tausenderpunkte in Zahlen
        self.thousands_pattern = re.compile(r'\b(\d{1,3})\.(\d{3})(?:\.(\d{3}))*\b')
    
    def fix_lists_and_enumerations(self, text: str) -> str:
        """
        Ersetzt Aufzählungen durch natürliche Sprache.
        - Bullets werden entfernt
        - Buchstaben (a, b, c...) -> erstens, zweitens...
        - Zahlen (1, 2, 3...) -> Punkt eins, Punkt zwei...
        """
        lines = text.split('\n')
        result_lines = []
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                result_lines.append(line)
                continue
            
            # Bullets entfernen
            if self.bullet_pattern.match(line):
                line = self.bullet_pattern.sub('', line, count=1)
            
            # Buchstaben-Aufzählungen
            letter_match = self.letter_enum_pattern.match(line)
            if letter_match:
                letter = letter_match.group(1).lower()
                number_words = {
                    'a': 'erstens', 'b': 'zweitens', 'c': 'drittens',
                    'd': 'viertens', 'e': 'fünftens', 'f': 'sechstens'
                }
                replacement = number_words.get(letter, f'Punkt {letter.upper()}')
                line = self.letter_enum_pattern.sub(f'{replacement}, ', line, count=1)
            
            # Zahlen-Aufzählungen
            number_match = self.number_enum_pattern.match(line)
            if number_match:
                number = int(number_match.group(1))
                if 1 <= number <= 10:
                    number_words = {
                        1: 'Punkt eins', 2: 'Punkt zwei', 3: 'Punkt drei',
                        4: 'Punkt vier', 5: 'Punkt fünf', 6: 'Punkt sechs',
                        7: 'Punkt sieben', 8: 'Punkt acht', 9: 'Punkt neun', 10: 'Punkt zehn'
                    }
                    replacement = number_words[number]
                else:
                    replacement = f'Punkt {number}'
                line = self.number_enum_pattern.sub(f'{replacement}, ', line, count=1)
            
            result_lines.append(line)
        
        return '\n'.join(result_lines)
    
    def fix_urls(self, text: str, mode: str = "domain") -> str:
        """
        Bereinigt URLs für natürliches Vorlesen.
        
        Args:
            mode: "domain" -> "Link zu example.com",
                  "generic" -> "Link",
                  "remove" -> komplett entfernen,
                  "keep" -> unverändert lassen
        """
        if mode == "keep":
            return text
        
        def url_replacer(match):
            url = match.group(0)
            if mode == "remove":
                return ""
            if mode == "generic":
                return "Link"
            # mode == "domain"
            try:
                from urllib.parse import urlparse
                parsed = urlparse(url)
                domain = parsed.netloc
                if domain.startswith('www.'):
                    domain = domain[4:]
                if domain:
                    return f"Link zu {domain}"
                return "Link"
            except Exception:
                return "Link"
        
        text = self.url_pattern.sub(url_replacer, text)
        
        # www.-Links separat behandeln
        if mode == "remove":
            text = self.www_pattern.sub("", text)
        elif mode == "generic":
            text = self.www_pattern.sub("Link", text)
        else:  # domain
            def www_replacer(match):
                url = match.group(0)
                domain = url.replace("https://", "").replace("http://", "").replace("www.", "").split('/')[0]
                if domain:
                    return f"Link zu {domain}"
                return "Link"
            text = self.www_pattern.sub(www_replacer, text)
        
        # Mehrfache Leerzeichen entfernen, die durch URL-Entfernung entstanden sein könnten
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def fix_quotes(self, text: str) -> str:
        """
        Ersetzt deutsche/typografische Anführungszeichen durch einfache,
        damit die TTS nicht 'größer als' oder 'kleiner als' liest.
        """
        text = self.german_quotes_open.sub('"', text)
        text = self.german_quotes_close.sub('"', text)
        return text
    
    def fix_thousands(self, text: str) -> str:
        """
        Entfernt Tausenderpunkte in Zahlen, damit die TTS sie korrekt vorliest.
        z.B. 1.234 -> 1234, 1.234.567 -> 1234567
        """
        def replacer(match):
            # Entferne alle Punkte aus der Zahl
            full_match = match.group(0)
            return full_match.replace('.', '')
        
        return self.thousands_pattern.sub(replacer, text)
    
    def remove_line_breaks_in_sentences(self, text: str) -> str:
        """
        Entfernt Zeilenumbrüche mitten im Satz
        Wichtig: Nur innerhalb von Sätzen, nicht zwischen Sätzen
        """
        # Schritt 1: Ersetze Bindestriche am Zeilenende
        # z.B. "Wort-\nende" -> "Wortende"
        text = self.hyphen_pattern.sub(r'\1\2', text)
        
        # Schritt 2: Ersetze einzelne Zeilenumbrüche durch Leerzeichen
        # ABER: Behalte doppelte Zeilenumbrüche für Absätze
        lines = text.split('\n')
        result_lines = []
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if not line:
                # Leere Zeile = Absatz
                result_lines.append('')
                i += 1
                continue
            
            # Prüfe ob die Zeile mit Satzzeichen endet
            ends_with_sentence = bool(self.sentence_endings.search(line[-3:]))
            
            if not ends_with_sentence and i + 1 < len(lines):
                # Kein Satzende -> nächste Zeile anhängen
                next_line = lines[i + 1].strip()
                if next_line and not next_line[0].isupper() and not next_line.startswith('Kapitel'):
                    # Kleiner Buchstabe am Anfang = gehört zusammen
                    line = line + ' ' + next_line
                    i += 1  # Überspringe nächste Zeile
            
            result_lines.append(line)
            i += 1
        
        # Verbinde mit Leerzeichen, Absätze bleiben erhalten
        return '\n'.join(result_lines)
    
    def normalize_whitespace(self, text: str) -> str:
        """
        Normalisiert Whitespace:
        - Mehrfache Leerzeichen -> Einzelne
        - Tabs -> Leerzeichen
        - Aber: Absätze (doppelte \n) bleiben
        """
        # Mehrfache Leerzeilen auf eine reduzieren
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # Pro Absatz Whitespace normalisieren
        paragraphs = [re.sub(r'\s+', ' ', p.strip()) for p in text.split('\n\n')]
        
        # Absätze mit doppelten Zeilenumbrüchen wieder zusammenfügen
        return '\n\n'.join(p for p in paragraphs if p)
    
    def fix_common_pdf_issues(self, text: str) -> str:
        """
        Repariert häufige PDF-Probleme
        """
        # Doppelte Leerzeichen nach Satzzeichen
        text = re.sub(r'([.!?,;:])\s+', r'\1 ', text)
        
        # Leerzeichen vor Satzzeichen
        text = re.sub(r'\s+([.!?,;:])', r'\1', text)
        
        # Doppelte Satzzeichen
        text = re.sub(r'\.{2,}', '...', text)  # ... bleibt
        text = re.sub(r'!{2,}', '!', text)
        text = re.sub(r'\?{2,}', '?', text)
        
        # Abkürzungen nicht als Satzende behandeln
        abbreviations = [
            (r'z\.\s*B\.', 'zum Beispiel'),
            (r'u\.\s*a\.', 'unter anderem'),
            (r'd\.\s*h\.', 'das heißt'),
            (r'v\.\s*a\.', 'vor allem'),
            (r'etc\.', 'et cetera'),
            (r'ca\.', 'circa'),
            (r'Dr\.', 'Doktor'),
            (r'Prof\.', 'Professor'),
            (r'Nr\.', 'Nummer'),
            (r'S\.', 'Seite'),
        ]
        
        for pattern, replacement in abbreviations:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text
    
    def split_into_sentences(self, text: str) -> List[str]:
        """
        Teilt Text in Sätze - intelligent!
        Erhält: Fragen, Ausrufe, Ellipsen
        """
        # Spezielles Muster für Satzerkennung
        # Berücksichtigt: . ! ? ...
        # Nicht nach: Zahlen (1. 2. 3.), Abkürzungen (Dr. Prof.)
        
        sentences = []
        current = ""
        
        # Split an Satzenden, aber behalte Satzzeichen
        parts = re.split(r'([.!?]+)', text)
        
        for i, part in enumerate(parts):
            if not part:
                continue
            
            current += part
            
            # Wenn dies Satzzeichen sind
            if re.match(r'^[.!?]+$', part):
                # Prüfe ob nächster Teil mit Großbuchstabe beginnt oder Ende
                if i + 1 < len(parts):
                    next_part = parts[i + 1].strip()
                    if not next_part or next_part[0].isupper() or next_part.startswith('['):
                        sentences.append(current.strip())
                        current = ""
        
        # Rest hinzufügen
        if current.strip():
            sentences.append(current.strip())
        
        return [s for s in sentences if len(s) > 5]  # Filter zu kurze
    
    def join_sentences(self, sentences: List[str]) -> str:
        """
        Fügt bereinigte Sätze zu einem fließenden Text zusammen.
        Edge-TTS fügt natürliche Pausen automatisch ein.
        """
        return ' '.join(sentences)
    
    def clean(self, text: str,
              clean_lists: bool = True,
              url_mode: str = "domain",
              fix_quotes: bool = True,
              fix_thousands: bool = True) -> str:
        """
        Hauptmethode: Bereinigt PDF-Text vollständig
        
        Args:
            text: Der zu bereinigende Text
            clean_lists: Aufzählungen in natürliche Sprache umwandeln
            url_mode: "domain", "generic", "remove", "keep"
            fix_quotes: Anführungszeichen bereinigen
            fix_thousands: Tausenderpunkte in Zahlen entfernen
        """
        if not text:
            return ""
        
        # Schritt 1: Aufzählungen bereinigen (muss VOR Zeilenumbruch-Entfernung passieren!)
        if clean_lists:
            text = self.fix_lists_and_enumerations(text)
        
        # Schritt 2: Zeilenumbrüche im Satz entfernen
        text = self.remove_line_breaks_in_sentences(text)
        
        # Schritt 3: Whitespace normalisieren
        text = self.normalize_whitespace(text)
        
        # Schritt 4: PDF-Probleme fixen
        text = self.fix_common_pdf_issues(text)
        
        # Schritt 5: URLs bereinigen
        if url_mode != "keep":
            text = self.fix_urls(text, mode=url_mode)
        
        # Schritt 6: Anführungszeichen bereinigen
        if fix_quotes:
            text = self.fix_quotes(text)
        
        # Schritt 7: Tausenderpunkte entfernen
        if fix_thousands:
            text = self.fix_thousands(text)
        
        # Schritt 8: In Sätze teilen
        sentences = self.split_into_sentences(text)
        
        # Schritt 9: Sätze zu fließendem Text zusammenfügen
        text = self.join_sentences(sentences)
        
        return text.strip()
    
    def get_stats(self, original: str, cleaned: str) -> dict:
        """
        Gibt Statistiken zur Bereinigung
        """
        return {
            'original_chars': len(original),
            'cleaned_chars': len(cleaned),
            'original_lines': original.count('\n'),
            'cleaned_lines': cleaned.count('\n'),
            'sentences': len(self.split_into_sentences(cleaned)),
            'reduction_percent': round((1 - len(cleaned) / len(original)) * 100, 1) if original else 0
        }


# Demo/Test
if __name__ == "__main__":
    cleaner = TextCleaner()
    
    # Test-Text mit problematischen Zeilenumbrüchen
    test_text = """Hast du dich jemals gefragt,
wie KI-Stimmen funktionieren?
Das ist unglaublich!

Seraphina ist eine der besten
deutschsprachigen Stimmen.
Sie klingt natürlich.

Er war wütend auf die schlechte
Verbindung... aber dann ging
alles wieder gut.

• Erster Punkt
• Zweiter Punkt
a) Option A
b) Option B
1. Schritt eins
2. Schritt zwei

Besuche uns unter https://www.example.com/path oder www.test.de.
Die Zahl 1.234 ist groß, und 5.678.900 ist riesig.
Sie sagte: „Das ist toll!"
"""
    
    print("=" * 60)
    print("VORHER (mit störenden Umbrüchen):")
    print("=" * 60)
    print(test_text)
    
    print("\n" + "=" * 60)
    print("NACHHER (flüssig):")
    print("=" * 60)
    
    cleaned = cleaner.clean(test_text)
    print(cleaned)
    
    print("\n" + "=" * 60)
    print("STATISTIK:")
    print("=" * 60)
    stats = cleaner.get_stats(test_text, cleaned)
    for key, value in stats.items():
        print(f"  {key}: {value}")
