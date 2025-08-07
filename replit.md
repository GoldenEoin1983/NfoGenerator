# StashApp to NFO Converter

## Overview

This is a command-line tool that converts StashApp JSON metadata files into Kodi/Jellyfin compatible NFO (XML) files. The application processes three types of media metadata: scenes (videos), performers (actors), and galleries (image collections). It features automatic data type detection, field mapping between StashApp and NFO formats, and generates properly formatted XML files with UTF-8 encoding for media center compatibility.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Core Components

**Modular Parser-Converter-Generator Pattern**: The application follows a clear separation of concerns with three main components:
- `StashParser`: Handles JSON file parsing and automatic data type detection
- `StashToNfoConverter`: Transforms StashApp data structures into NFO-compatible formats
- `NfoGenerator`: Creates properly formatted XML output for media centers

**Data Type Detection System**: Implements intelligent auto-detection by analyzing JSON structure and presence of specific fields (file/duration for scenes, gender/birthdate for performers, folder/scenes for galleries).

**Field Mapping Strategy**: Uses a mapping approach to convert StashApp-specific fields to standard NFO XML tags, including rating scale conversion (1-5 to 0-10) and metadata normalization.

**XML Generation Architecture**: Utilizes Python's xml.etree.ElementTree for XML creation with optional pretty-printing via minidom for human-readable output.

### Design Patterns

**Factory Pattern**: The converter and generator classes use factory-like methods to handle different data types (scene, performer, gallery) with type-specific processing logic.

**Command-Line Interface**: Built with argparse for flexible command-line operation with auto-detection capabilities and configurable output paths.

**Error Handling Strategy**: Implements comprehensive error handling for file operations, JSON parsing, and data conversion with meaningful error messages.

## External Dependencies

**Python Standard Library**: 
- `xml.etree.ElementTree` and `xml.dom.minidom` for XML processing
- `json` for JSON parsing
- `argparse` for command-line interface
- `pathlib` for file system operations

**No Third-Party Dependencies**: The application is designed to run with only Python 3.6+ standard library components, ensuring easy deployment and minimal dependency management.

**Target Media Centers**: 
- Kodi NFO format compatibility
- Jellyfin NFO format compatibility
- UTF-8 encoding support for international character sets