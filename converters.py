"""
Converters for transforming StashApp data to NFO format.
"""

import base64
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Union


class StashToNfoConverter:
    """Converts StashApp JSON data to NFO-compatible format."""
    
    def __init__(self):
        """Initialize the converter."""
        self.extracted_images: List[Dict[str, Union[str, int]]] = []

    def convert(self, stash_data: Dict[str, Any],
                data_type: str) -> Dict[str, Any]:
        """
        Convert StashApp data to NFO format.
        
        Args:
            stash_data: Parsed StashApp JSON data
            data_type: Type of data ('scene', 'performer', 'gallery')
            
        Returns:
            NFO-compatible data structure
        """
        if data_type == 'scene':
            return self._convert_scene(stash_data)
        elif data_type == 'performer':
            return self._convert_performer(stash_data)
        elif data_type == 'gallery':
            return self._convert_gallery(stash_data)
        else:
            raise ValueError(f"Unsupported data type: {data_type}")

    def _convert_scene(self, scene_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert StashApp scene data to movie NFO format."""
        nfo_data = {}

        # Basic metadata
        nfo_data['title'] = scene_data.get('title', '')
        nfo_data['originaltitle'] = scene_data.get('title', '')
        nfo_data['plot'] = scene_data.get('details', '')

        # Rating (convert from StashApp rating to 0-10 scale)
        rating = scene_data.get('rating')
        if rating is not None:
            # Assume StashApp rating is 1-5, convert to 0-10
            try:
                nfo_data['userrating'] = float(rating) * 2
            except (ValueError, TypeError):
                nfo_data['userrating'] = 0
        else:
            nfo_data['userrating'] = 0

        # Date handling
        date_str = scene_data.get('date')
        if date_str:
            nfo_data['premiered'] = self._convert_date(date_str)
            try:
                year = datetime.strptime(date_str, '%Y-%m-%d').year
                nfo_data['year'] = year
            except (ValueError, TypeError):
                pass

        # Studio
        nfo_data['studio'] = scene_data.get('studio', '')

        # URL as unique ID
        url = scene_data.get('url')
        if url:
            nfo_data['uniqueid'] = {
                'type': 'stash',
                'value': url,
                'default': True
            }

        # Genres from tags
        tags = scene_data.get('tags', [])
        if isinstance(tags, list):
            nfo_data['genres'] = tags

        # Performers as actors
        performers = scene_data.get('performers', [])
        if isinstance(performers, list):
            nfo_data['actors'] = self._convert_performers_to_actors(performers)

        # File information for runtime
        file_info = scene_data.get('file', {})
        if isinstance(file_info, dict):
            duration = file_info.get('duration')
            if duration:
                try:
                    # Convert duration to minutes (assuming duration is in seconds)
                    nfo_data['runtime'] = int(float(duration) / 60)
                except (ValueError, TypeError):
                    pass

        return nfo_data

    def _convert_performer(self, performer_data: Dict[str,
                                                      Any]) -> Dict[str, Any]:
        """Convert StashApp performer data to actor NFO format."""
        nfo_data = {}

        # Basic information
        nfo_data['name'] = performer_data.get('name', '')
        nfo_data['biography'] = self._build_performer_biography(performer_data)

        # Birth date
        birthdate = performer_data.get('birthdate')
        if birthdate:
            nfo_data['birthdate'] = self._convert_date(birthdate)

        # Additional metadata that can be included in biography
        nfo_data['details'] = {
            'gender': performer_data.get('gender', ''),
            'ethnicity': performer_data.get('ethnicity', ''),
            'country': performer_data.get('country', ''),
            'eye_color': performer_data.get('eye_color', ''),
            'height': performer_data.get('height', ''),
            'measurements': performer_data.get('measurements', ''),
            'tattoos': performer_data.get('tattoos', ''),
            'piercings': performer_data.get('piercings', ''),
            'aliases': performer_data.get('aliases', [])
        }

        # Social media
        nfo_data['social'] = {
            'url': performer_data.get('url', ''),
            'twitter': performer_data.get('twitter', ''),
            'instagram': performer_data.get('instagram', '')
        }

        return nfo_data

    def _convert_gallery(self, gallery_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert StashApp gallery data to NFO format (treated as movie)."""
        nfo_data = {}

        # Basic metadata
        nfo_data['title'] = gallery_data.get('title', '')
        nfo_data['originaltitle'] = gallery_data.get('title', '')
        nfo_data['plot'] = gallery_data.get('details', '')

        # Date handling
        date_str = gallery_data.get('date')
        if date_str:
            nfo_data['premiered'] = self._convert_date(date_str)
            try:
                year = datetime.strptime(date_str, '%Y-%m-%d').year
                nfo_data['year'] = year
            except (ValueError, TypeError):
                pass

        # Studio
        nfo_data['studio'] = gallery_data.get('studio', '')

        # URL as unique ID
        url = gallery_data.get('url')
        if url:
            nfo_data['uniqueid'] = {
                'type': 'stash',
                'value': url,
                'default': True
            }

        # Genres from tags
        tags = gallery_data.get('tags', [])
        if isinstance(tags, list):
            nfo_data['genres'] = tags

        # Performers as actors
        performers = gallery_data.get('performers', [])
        if isinstance(performers, list):
            nfo_data['actors'] = self._convert_performers_to_actors(performers)

        # Mark as gallery type
        nfo_data['media_type'] = 'gallery'

        return nfo_data

    def _convert_performers_to_actors(
            self, performers: List[Union[str,
                                         Dict[str,
                                              Any]]]) -> List[Dict[str, Any]]:
        """Convert performers list to actors format for NFO."""
        actors = []

        for i, performer in enumerate(performers):
            actor: Dict[str, Any] = {'order': i}

            if isinstance(performer, str):
                actor['name'] = performer
                actor['role'] = ''
            elif isinstance(performer, dict):
                actor['name'] = performer.get('name', '')
                actor['role'] = performer.get('role', '')
            else:
                continue

            actors.append(actor)

        return actors

    def _convert_date(self, date_str: str) -> str:
        """
        Convert date string to NFO format (YYYY-MM-DD).
        
        Args:
            date_str: Date string in various formats
            
        Returns:
            Date string in YYYY-MM-DD format, or original string if conversion fails
        """
        if not date_str:
            return ''

        # Common date formats to try
        date_formats = [
            '%Y-%m-%d',  # 2023-12-25
            '%Y-%m-%dT%H:%M:%S',  # 2023-12-25T10:30:00
            '%Y-%m-%dT%H:%M:%S%z',  # 2023-12-25T10:30:00Z
            '%d/%m/%Y',  # 25/12/2023
            '%m/%d/%Y',  # 12/25/2023
            '%d-%m-%Y',  # 25-12-2023
            '%m-%d-%Y',  # 12-25-2023
        ]

        for fmt in date_formats:
            try:
                dt = datetime.strptime(
                    date_str.split('T')[0],
                    fmt.split('T')[0])
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                continue

        # If no format matches, return original string
        return date_str

    def _build_performer_biography(self, performer_data: Dict[str,
                                                              Any]) -> str:
        """Build a biography string from performer data."""
        bio_parts = []

        # Basic information
        gender = performer_data.get('gender')
        if gender:
            bio_parts.append(f"Gender: {gender}")

        ethnicity = performer_data.get('ethnicity')
        if ethnicity:
            bio_parts.append(f"Ethnicity: {ethnicity}")

        country = performer_data.get('country')
        if country:
            bio_parts.append(f"Country: {country}")

        # Physical attributes
        height = performer_data.get('height')
        if height:
            bio_parts.append(f"Height: {height}")

        measurements = performer_data.get('measurements')
        if measurements:
            bio_parts.append(f"Measurements: {measurements}")

        eye_color = performer_data.get('eye_color')
        if eye_color:
            bio_parts.append(f"Eye Color: {eye_color}")

        # Career information
        career_length = performer_data.get('career_length')
        if career_length:
            bio_parts.append(f"Career Length: {career_length}")

        # Body modifications
        tattoos = performer_data.get('tattoos')
        if tattoos:
            bio_parts.append(f"Tattoos: {tattoos}")

        piercings = performer_data.get('piercings')
        if piercings:
            bio_parts.append(f"Piercings: {piercings}")

        # Aliases
        aliases = performer_data.get('aliases', [])
        if aliases and isinstance(aliases, list):
            bio_parts.append(f"Aliases: {', '.join(aliases)}")

        return '\n'.join(bio_parts)
    
    def extract_images(self, stash_data: Dict[str, Any], output_path: Path) -> List[str]:
        """
        Extract and save base64 encoded images from StashApp data.
        
        Args:
            stash_data: Parsed StashApp JSON data
            output_path: Path for the output NFO file (used to determine image save location)
            
        Returns:
            List of saved image filenames
        """
        self.extracted_images.clear()
        saved_images = []
        
        # Define possible image fields in StashApp data
        image_fields = {
            'cover': 'poster',     # Cover image -> poster.jpg
            'image': 'thumb',      # Generic image -> thumb.jpg
            'poster': 'poster',    # Poster image -> poster.jpg
            'thumbnail': 'thumb',  # Thumbnail -> thumb.jpg
            'fanart': 'fanart'     # Fanart -> fanart.jpg
        }
        
        output_dir = output_path.parent
        base_name = output_path.stem
        
        for field_name, image_type in image_fields.items():
            if field_name in stash_data:
                image_data = stash_data[field_name]
                if isinstance(image_data, str) and image_data:
                    saved_file = self._save_base64_image(image_data, output_dir, base_name, image_type)
                    if saved_file:
                        saved_images.append(saved_file)
        
        return saved_images
    
    def _save_base64_image(self, image_data: str, output_dir: Path, base_name: str, image_type: str) -> Optional[str]:
        """
        Save a base64 encoded image to disk.
        
        Args:
            image_data: Base64 encoded image string
            output_dir: Directory to save the image
            base_name: Base filename (without extension)
            image_type: Type of image (poster, thumb, fanart)
            
        Returns:
            Filename of saved image, or None if save failed
        """
        try:
            # Remove data URL prefix if present (e.g., "data:image/jpeg;base64,")
            if image_data.startswith('data:'):
                image_data = image_data.split(',', 1)[1]
            
            # Decode base64 data
            image_bytes = base64.b64decode(image_data)
            
            # Detect image format from header
            image_format = self._detect_image_format(image_bytes)
            if not image_format:
                return None
            
            # Create filename
            if image_type in ['poster', 'fanart']:
                filename = f"{image_type}.{image_format}"
            else:
                filename = f"{base_name}-{image_type}.{image_format}"
            
            image_path = output_dir / filename
            
            # Save image file
            with open(image_path, 'wb') as f:
                f.write(image_bytes)
            
            # Store extraction info
            self.extracted_images.append({
                'type': image_type,
                'filename': filename,
                'size': len(image_bytes)
            })
            
            return filename
            
        except Exception as e:
            # Silently skip failed image extractions
            return None
    
    def _detect_image_format(self, image_bytes: bytes) -> Optional[str]:
        """
        Detect image format from file header.
        
        Args:
            image_bytes: Raw image data
            
        Returns:
            Image format extension (jpg, png, gif, webp) or None
        """
        if not image_bytes:
            return None
        
        # Check common image format headers
        if image_bytes.startswith(b'\xff\xd8\xff'):
            return 'jpg'
        elif image_bytes.startswith(b'\x89PNG\r\n\x1a\n'):
            return 'png'
        elif image_bytes.startswith(b'GIF87a') or image_bytes.startswith(b'GIF89a'):
            return 'gif'
        elif image_bytes.startswith(b'RIFF') and b'WEBP' in image_bytes[:12]:
            return 'webp'
        elif image_bytes.startswith(b'BM'):
            return 'bmp'
        
        # Default to jpg if unknown
        return 'jpg'
