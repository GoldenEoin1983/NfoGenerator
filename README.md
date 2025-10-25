# StashApp to NFO Converter

A command-line tool that converts StashApp JSON metadata files into Kodi/Jellyfin compatible NFO files.

## Features

- **Multiple Data Types**: Supports StashApp scenes, performers, and galleries
- **Auto-Detection**: Automatically detects the type of StashApp data
- **Kodi/Jellyfin Compatible**: Generates properly formatted NFO files with UTF-8 encoding
- **Field Mapping**: Maps StashApp fields to appropriate NFO XML tags
- **Error Handling**: Comprehensive error handling for invalid files and operations
- **Flexible Output**: Configurable output formatting and encoding

### Recent changes
- Added support for a `tagline` field on scene JSON: it is carried through the converter and emitted as a `<tagline>` element in movie NFO files.

## Installation

No installation required. Just ensure you have Python 3.6+ installed.

## Usage

### Basic Usage

```bash
# Convert a scene JSON file
python stash_to_nfo.py scene.json

# Specify output file
python stash_to_nfo.py scene.json output.nfo

# Convert performer data
python stash_to_nfo.py --type performer performer.json

# Convert gallery data
python stash_to_nfo.py --type gallery gallery.json
