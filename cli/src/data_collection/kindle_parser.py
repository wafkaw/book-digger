"""
Kindle HTML parser for extracting reading notes and highlights
"""
import re
import html
from typing import List, Optional, Tuple
from datetime import datetime
from bs4 import BeautifulSoup, Tag
import logging

from ..config.models import (
    Book, BookMetadata, Highlight, HighlightType, NoteType, Location
)


class KindleParser:
    """Parser for Kindle HTML export files"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def parse_file(self, file_path: str) -> Book:
        """Parse Kindle HTML file and return Book object"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return self.parse_html_content(content)
            
        except Exception as e:
            self.logger.error(f"Error parsing file {file_path}: {e}")
            raise
    
    def parse_html_content(self, html_content: str) -> Book:
        """Parse HTML content and extract book data"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract book metadata
        metadata = self._extract_metadata(soup)
        
        # Extract highlights
        highlights = self._extract_highlights(soup)
        
        # Create book object
        book = Book(
            metadata=metadata,
            highlights=highlights,
            export_date=datetime.now()
        )
        
        self.logger.info(f"Parsed book: {metadata.title} with {len(highlights)} highlights")
        return book
    
    def _extract_metadata(self, soup: BeautifulSoup) -> BookMetadata:
        """Extract book metadata from HTML"""
        # Find book title
        title_element = soup.find('div', class_='bookTitle')
        if not title_element:
            raise ValueError("Book title not found in HTML")
        
        title_string = title_element.get_text().strip()
        return BookMetadata.from_title_string(title_string)
    
    def _extract_highlights(self, soup: BeautifulSoup) -> List[Highlight]:
        """Extract all highlights from HTML"""
        highlights = []
        
        # Find all section headings
        sections = soup.find_all('div', class_='sectionHeading')
        
        current_section = None
        
        for section in sections:
            section_text = section.get_text().strip()
            current_section = section_text
            
            # Find all highlights in this section
            next_element = section.next_sibling
            
            while next_element:
                if next_element.name == 'div' and 'noteHeading' in next_element.get('class', []):
                    # This is a highlight heading
                    highlight = self._parse_highlight(next_element, current_section)
                    if highlight:
                        highlights.append(highlight)
                
                elif next_element.name == 'div' and 'sectionHeading' in next_element.get('class', []):
                    # We've reached the next section
                    break
                
                next_element = next_element.next_sibling
        
        return highlights
    
    def _parse_highlight(self, heading_element: Tag, section: str) -> Optional[Highlight]:
        """Parse a single highlight from heading and following text"""
        try:
            # Parse heading to get highlight type and location
            heading_text = heading_element.get_text().strip()
            
            # Extract highlight type
            highlight_type = self._extract_highlight_type(heading_text)
            if not highlight_type:
                return None
            
            # Extract location information
            location = self._extract_location(heading_text)
            if not location:
                return None
            
            # Find the highlight text (next sibling with noteText class)
            text_element = heading_element.find_next_sibling('div', class_='noteText')
            if not text_element:
                return None
            
            content = text_element.get_text().strip()
            content = html.unescape(content)
            
            return Highlight(
                content=content,
                location=location,
                highlight_type=highlight_type,
                section=section,
                note_type=NoteType.HIGHLIGHT
            )
            
        except Exception as e:
            self.logger.warning(f"Error parsing highlight: {e}")
            return None
    
    def _extract_highlight_type(self, heading_text: str) -> Optional[HighlightType]:
        """Extract highlight type from heading text"""
        # Look for highlight color classes in the heading
        color_pattern = r'highlight_(\w+)'
        match = re.search(color_pattern, heading_text)
        
        if match:
            color_name = match.group(1).upper()
            try:
                return HighlightType[color_name]
            except KeyError:
                self.logger.warning(f"Unknown highlight color: {color_name}")
                return HighlightType.YELLOW  # Default to yellow
        
        return HighlightType.YELLOW
    
    def _extract_location(self, heading_text: str) -> Optional[Location]:
        """Extract location information from heading text"""
        # Pattern: "Highlight(yellow) - Page 29 · Location 364"
        location_pattern = r'Page\s+(\d+)\s*·\s*Location\s+(\d+)'
        match = re.search(location_pattern, heading_text)
        
        if match:
            page = int(match.group(1))
            position = int(match.group(2))
            return Location(page=page, position=position)
        
        # Alternative pattern: "Location 1234"
        alt_pattern = r'Location\s+(\d+)'
        match = re.search(alt_pattern, heading_text)
        if match:
            position = int(match.group(1))
            return Location(page=0, position=position)
        
        return None
    
    def parse_multiple_files(self, file_paths: List[str]) -> List[Book]:
        """Parse multiple Kindle HTML files"""
        books = []
        
        for file_path in file_paths:
            try:
                book = self.parse_file(file_path)
                books.append(book)
            except Exception as e:
                self.logger.error(f"Failed to parse {file_path}: {e}")
                continue
        
        return books
    
    def validate_html_structure(self, html_content: str) -> bool:
        """Validate that the HTML has expected Kindle structure"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Check for required elements
        required_elements = [
            ('div', 'bookTitle'),
            ('div', 'authors'),
            ('div', 'sectionHeading'),
            ('div', 'noteHeading'),
            ('div', 'noteText')
        ]
        
        for tag_name, class_name in required_elements:
            elements = soup.find_all(tag_name, class_=class_name)
            if not elements:
                self.logger.warning(f"Required element not found: {tag_name}.{class_name}")
                return False
        
        return True