"""
NFO XML file generator for Kodi/Jellyfin compatibility.
"""

import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Optional
from xml.dom import minidom


class NfoGenerator:
    """Generates NFO XML files from converted data."""
    
    def __init__(self, encoding: str = 'utf-8', pretty_print: bool = True):
        """
        Initialize the NFO generator.
        
        Args:
            encoding: XML encoding (default: utf-8)
            pretty_print: Whether to format XML with indentation
        """
        self.encoding = encoding
        self.pretty_print = pretty_print
    
    def generate(self, nfo_data: Dict[str, Any], data_type: str) -> str:
        """
        Generate NFO XML from converted data.
        
        Args:
            nfo_data: Converted NFO data structure
            data_type: Type of data ('scene', 'performer', 'gallery')
            
        Returns:
            XML string in NFO format
        """
        if data_type in ['scene', 'gallery']:
            return self._generate_movie_nfo(nfo_data)
        elif data_type == 'performer':
            return self._generate_actor_nfo(nfo_data)
        else:
            raise ValueError(f"Unsupported data type: {data_type}")
    
    def _generate_movie_nfo(self, nfo_data: Dict[str, Any]) -> str:
        """Generate movie NFO XML."""
        root = ET.Element('movie')
        
        # Basic metadata
        self._add_text_element(root, 'title', nfo_data.get('title', ''))
        self._add_text_element(root, 'originaltitle', nfo_data.get('originaltitle', ''))
        self._add_text_element(root, 'plot', nfo_data.get('plot', ''))
        
        # Rating
        userrating = nfo_data.get('userrating', 0)
        self._add_text_element(root, 'userrating', str(userrating))
        
        # Date information
        premiered = nfo_data.get('premiered')
        if premiered:
            self._add_text_element(root, 'premiered', premiered)
        
        year = nfo_data.get('year')
        if year:
            self._add_text_element(root, 'year', str(year))
        
        # Studio
        studio = nfo_data.get('studio')
        if studio:
            self._add_text_element(root, 'studio', studio)
        
        # Runtime
        runtime = nfo_data.get('runtime')
        if runtime:
            self._add_text_element(root, 'runtime', str(runtime))
        
        # Unique ID
        uniqueid_data = nfo_data.get('uniqueid')
        if uniqueid_data and isinstance(uniqueid_data, dict):
            uniqueid_elem = ET.SubElement(root, 'uniqueid')
            uniqueid_elem.set('type', uniqueid_data.get('type', 'stash'))
            if uniqueid_data.get('default'):
                uniqueid_elem.set('default', 'true')
            uniqueid_elem.text = uniqueid_data.get('value', '')
        
        # Genres
        genres = nfo_data.get('genres', [])
        for genre in genres:
            if genre:  # Skip empty genres
                self._add_text_element(root, 'genre', genre)
        
        # Tags (same as genres for NFO format)
        for genre in genres:
            if genre:
                self._add_text_element(root, 'tag', genre)
        
        # Actors
        actors = nfo_data.get('actors', [])
        for actor_data in actors:
            if isinstance(actor_data, dict):
                actor_elem = ET.SubElement(root, 'actor')
                
                name = actor_data.get('name', '')
                if name:
                    self._add_text_element(actor_elem, 'name', name)
                
                role = actor_data.get('role', '')
                if role:
                    self._add_text_element(actor_elem, 'role', role)
                
                order = actor_data.get('order')
                if order is not None:
                    self._add_text_element(actor_elem, 'order', str(order))
        
        return self._format_xml(root)
    
    def _generate_actor_nfo(self, nfo_data: Dict[str, Any]) -> str:
        """Generate actor/performer NFO XML."""
        root = ET.Element('actor')
        
        # Basic information
        self._add_text_element(root, 'name', nfo_data.get('name', ''))
        
        biography = nfo_data.get('biography', '')
        if biography:
            self._add_text_element(root, 'biography', biography)
        
        birthdate = nfo_data.get('birthdate')
        if birthdate:
            self._add_text_element(root, 'birthdate', birthdate)
        
        # Additional details as custom elements
        details = nfo_data.get('details', {})
        if isinstance(details, dict):
            for key, value in details.items():
                if value:  # Only add non-empty values
                    if isinstance(value, list):
                        for item in value:
                            if item:
                                self._add_text_element(root, key, str(item))
                    else:
                        self._add_text_element(root, key, str(value))
        
        # Social media information
        social = nfo_data.get('social', {})
        if isinstance(social, dict):
            for key, value in social.items():
                if value:
                    self._add_text_element(root, key, str(value))
        
        return self._format_xml(root)
    
    def _add_text_element(self, parent: ET.Element, tag: str, text: str) -> ET.Element:
        """
        Add a text element to the parent.
        
        Args:
            parent: Parent XML element
            tag: Tag name
            text: Text content
            
        Returns:
            Created element
        """
        elem = ET.SubElement(parent, tag)
        elem.text = text if text else ''
        return elem
    
    def _format_xml(self, root: ET.Element) -> str:
        """
        Format XML element as string with proper encoding and formatting.
        
        Args:
            root: Root XML element
            
        Returns:
            Formatted XML string
        """
        # Convert to string
        xml_str = ET.tostring(root, encoding='unicode')
        
        if self.pretty_print:
            # Use minidom for pretty printing
            dom = minidom.parseString(xml_str)
            pretty_xml = dom.documentElement.toprettyxml(indent='  ')
            
            # Remove empty lines and fix formatting
            lines = [line for line in pretty_xml.split('\n') if line.strip()]
            xml_str = '\n'.join(lines)
        
        # Add XML declaration
        xml_declaration = f'<?xml version="1.0" encoding="{self.encoding}" standalone="yes" ?>'
        
        if self.pretty_print:
            return f"{xml_declaration}\n{xml_str}"
        else:
            return f"{xml_declaration}{xml_str}"
