"""
PDF Parser - Extrahiert intelligent Text aus PDFs
Filtert: Fussnoten, Seitenzahlen, Header/Footer
"""

import re
from dataclasses import dataclass
from typing import List, Dict, Tuple
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    print("PyMuPDF nicht installiert. Installiere mit: pip install PyMuPDF")
    raise


@dataclass
class TextBlock:
    """Repraesentiert einen Textblock mit Metadaten"""
    text: str
    font_size: float
    is_bold: bool
    y_position: float
    page_num: int
    block_type: str = "text"  # 'header', 'footer', 'footnote', 'main', 'title'


class PDFIntelligentParser:
    """
    Intelligenter PDF Parser der Layout analysiert
    und nur relevanten Text extrahiert
    """
    
    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)
        self.doc = fitz.open(pdf_path)
        self.text_blocks: List[TextBlock] = []
        self.stats = {
            'pages': len(self.doc),
            'blocks_total': 0,
            'blocks_filtered': 0
        }
    
    def _is_likely_header_footer(self, block: TextBlock, page_height: float) -> bool:
        """
        Erkennt Header/Footer basierend auf Position
        Header: Oben 10% der Seite
        Footer: Unten 10% der Seite
        """
        top_margin = page_height * 0.1
        bottom_margin = page_height * 0.9
        
        # Sehr kleine Schrift oft = Header/Footer/Seitenzahl
        if block.font_size < 8:
            return True
            
        # Position-basiert
        if block.y_position < top_margin or block.y_position > bottom_margin:
            # Zusaetzlich: Sehr kurzer Text = wahrscheinlich Seitenzahl
            if len(block.text.strip()) < 20:
                return True
                
        return False
    
    def _is_likely_footnote(self, block: TextBlock) -> bool:
        """
        Erkennt Fussnoten:
        - Beginnt mit Zahl oder Symbol
        - Sehr kleine Schrift
        - Oft am Seitenende
        """
        text = block.text.strip()
        
        # Kleine Schrift + beginnt mit Nummer = Fussnote
        if block.font_size < 9:
            if re.match(r'^\d+\s', text) or re.match(r'^\[\d+\]', text):
                return True
                
        return False
    
    def _is_noise(self, text: str) -> bool:
        """Filtert stoerende Elemente"""
        noise_patterns = [
            r'^Seite\s+\d+\s+von\s+\d+$',
            r'^\d+\s*/\s*\d+$',
            r'^\d+$',  # Nur eine Zahl
            r'^Kapitel\s+\d+',  # Kapitelueberschriften (optional)
            r'^Copyright',
            r'^(C)\s*\d{4}',
            r'^www\.',  # URLs
            r'@.*\.com',  # Email
        ]
        
        for pattern in noise_patterns:
            if re.match(pattern, text.strip(), re.IGNORECASE):
                return True
        return False
    
    def parse_page(self, page_num: int) -> List[TextBlock]:
        """Parst eine einzelne Seite"""
        page = self.doc[page_num]
        blocks = page.get_text("dict")["blocks"]
        page_height = page.rect.height
        
        parsed_blocks = []
        
        for block in blocks:
            if "lines" not in block:
                continue
                
            for line in block["lines"]:
                for span in line["spans"]:
                    text = span["text"].strip()
                    if not text or len(text) < 2:
                        continue
                    
                    # Erstelle Block
                    text_block = TextBlock(
                        text=text,
                        font_size=span["size"],
                        is_bold="bold" in span["font"].lower(),
                        y_position=line["bbox"][1],  # Y-Position
                        page_num=page_num + 1
                    )
                    
                    # Klassifiziere Block
                    if self._is_noise(text):
                        text_block.block_type = "noise"
                    elif self._is_likely_header_footer(text_block, page_height):
                        text_block.block_type = "header_footer"
                    elif self._is_likely_footnote(text_block):
                        text_block.block_type = "footnote"
                    elif text_block.font_size > 14 or text_block.is_bold:
                        text_block.block_type = "title"
                    else:
                        text_block.block_type = "main"
                    
                    parsed_blocks.append(text_block)
        
        return parsed_blocks
    
    def extract_text(self, 
                     include_headers: bool = False,
                     include_footnotes: bool = False,
                     include_titles: bool = True) -> str:
        """
        Extrahiert gefilterten Text aus dem PDF
        
        Args:
            include_headers: Header/Footer/Seitenzahlen einbeziehen
            include_footnotes: Fussnoten einbeziehen
            include_titles: Ueberschriften einbeziehen
        """
        all_blocks = []
        
        for page_num in range(len(self.doc)):
            blocks = self.parse_page(page_num)
            all_blocks.extend(blocks)
        
        self.stats['blocks_total'] = len(all_blocks)
        
        # Filter anwenden
        filtered_blocks = []
        for block in all_blocks:
            if block.block_type == "noise":
                continue
            if block.block_type == "header_footer" and not include_headers:
                continue
            if block.block_type == "footnote" and not include_footnotes:
                continue
            if block.block_type == "title" and not include_titles:
                continue
            
            filtered_blocks.append(block)
        
        self.stats['blocks_filtered'] = len(filtered_blocks)
        
        # Sortiere nach Seite und Position
        filtered_blocks.sort(key=lambda b: (b.page_num, b.y_position))
        
        # Baue Text zusammen
        lines = []
        for block in filtered_blocks:
            text = block.text
            
            # Fuege Pause nach Titeln ein
            if block.block_type == "title":
                text += "\n\n"
            
            lines.append(text)
        
        return "\n".join(lines)
    
    def get_structure(self) -> Dict:
        """Gibt die erkannte Struktur zurueck"""
        structure = {
            'pages': len(self.doc),
            'estimated_duration_min': 0,
            'chapters': []
        }
        
        # Suche nach Kapitelueberschriften
        all_blocks = []
        for page_num in range(len(self.doc)):
            blocks = self.parse_page(page_num)
            all_blocks.extend(blocks)
        
        # Extrahiere potenzielle Kapitel (grosse, fette Schrift)
        potential_chapters = [
            b for b in all_blocks 
            if b.block_type == "title" or (b.font_size > 16 and b.is_bold)
        ]
        
        structure['chapters'] = [b.text for b in potential_chapters[:20]]
        
        # Schaetze Dauer (ca. 150 Woerter pro Minute)
        filtered_text = self.extract_text()
        word_count = len(filtered_text.split())
        structure['estimated_duration_min'] = word_count // 150
        structure['word_count'] = word_count
        
        return structure
    
    def close(self):
        """Schliesst das PDF"""
        self.doc.close()


# Test
if __name__ == "__main__":
    # Beispiel-Test
    import sys
    
    if len(sys.argv) > 1:
        pdf_file = sys.argv[1]
        parser = PDFIntelligentParser(pdf_file)
        
        print("PDF wird analysiert...")
        structure = parser.get_structure()
        
        print(f"\nSeiten: {structure['pages']}")
        print(f"Geschaetzte Dauer: {structure['estimated_duration_min']} Minuten")
        print(f"Woerter: {structure['word_count']}")
        print(f"\nErkannte Kapitel:")
        for i, chapter in enumerate(structure['chapters'][:5], 1):
            print(f"  {i}. {chapter[:60]}...")
        
        # Extrahiere Text
        text = parser.extract_text()
        print(f"\nExtrahierter Text (erste 500 Zeichen):")
        print(text[:500])
        
        parser.close()
    else:
        print("Usage: python pdf_parser.py <pdf_file>")
