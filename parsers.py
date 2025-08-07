"""
StashApp JSON parsers for different data types.
"""

import json
from pathlib import Path
from typing import Dict, Any, Union


class StashParser:
    """Parser for StashApp JSON files."""
    
    def parse_file(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Parse a StashApp JSON file.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            Parsed JSON data as dictionary
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            json.JSONDecodeError: If the file contains invalid JSON
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def detect_type(self, data: Dict[str, Any]) -> str:
        """
        Auto-detect the type of StashApp data.
        
        Args:
            data: Parsed JSON data
            
        Returns:
            Detected type: 'scene', 'performer', 'gallery', or 'unknown'
        """
        # Check for scene-specific fields
        if any(key in data for key in ['file', 'duration', 'performers']):
            if 'file' in data and isinstance(data['file'], dict):
                return 'scene'
        
        # Check for performer-specific fields
        if any(key in data for key in ['gender', 'birthdate', 'ethnicity', 'measurements']):
            return 'performer'
        
        # Check for gallery-specific fields
        if any(key in data for key in ['folder', 'scenes']) and 'performers' in data:
            return 'gallery'
        
        # Default to scene if has basic metadata fields
        if any(key in data for key in ['title', 'studio', 'tags', 'performers']):
            return 'scene'
        
        return 'unknown'
    
    def validate_scene_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate that the data contains expected scene fields.
        
        Args:
            data: Parsed JSON data
            
        Returns:
            True if data appears to be valid scene data
        """
        # At minimum, a scene should have a title or file information
        return 'title' in data or 'file' in data
    
    def validate_performer_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate that the data contains expected performer fields.
        
        Args:
            data: Parsed JSON data
            
        Returns:
            True if data appears to be valid performer data
        """
        # A performer must have a name
        return 'name' in data
    
    def validate_gallery_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate that the data contains expected gallery fields.
        
        Args:
            data: Parsed JSON data
            
        Returns:
            True if data appears to be valid gallery data
        """
        # A gallery should have a title or folder information
        return 'title' in data or 'folder' in data
