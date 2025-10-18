# Copilot Instructions for NfoGenerator

This guide helps AI coding agents understand the key aspects of the NfoGenerator project, a Python tool that converts StashApp metadata to Kodi/Jellyfin NFO files.

## Project Architecture

The codebase follows a modular design with clear separation of concerns:

- `stash_to_nfo.py`: Main entry point and CLI interface
- `parsers.py`: Handles parsing StashApp JSON data
- `converters.py`: Converts StashApp data to NFO format
- `nfo_generator.py`: Generates XML NFO files
- `stash_api.py`: StashApp GraphQL API client

### Key Data Flows

1. Input → Parser → Converter → NFO Generator → Output
2. API Client → StashApp → Parser → (same flow as above)

## Development Environment

- Python 3.11+ required
- Key dependency: `stashapp-tools>=0.2.58` for API integration
- No build step needed - direct Python execution

## Project Conventions

### Input Handling
```python
# Three supported input methods:
python stash_to_nfo.py scene.json                  # Direct JSON file
python stash_to_nfo.py --stash-id 123             # Query by ID
python stash_to_nfo.py --search "query string"     # Search StashApp
```

### Error Handling
- Use explicit error types and messages
- Validate data early in the pipeline
- Example in `nfo_generator.py`:
```python
if data_type not in ['scene', 'performer', 'gallery']:
    raise ValueError(f"Unsupported data type: {data_type}")
```

### XML Generation
- Use ElementTree for XML manipulation
- Prefer explicit tag creation over string templates
- UTF-8 encoding required for NFO compatibility

## Integration Points

1. StashApp GraphQL API:
   - Authentication via API key or username/password
   - Configurable host/port/scheme
   - Implements key queries for scenes, performers, galleries

2. NFO XML Schema:
   - Follows Kodi/Jellyfin NFO format requirements
   - Supports movie and actor metadata types
   - See `nfo_generator.py` for supported fields

## Testing and Debugging

- Input validation failures appear in CLI output
- API connection issues include detailed error messages
- XML validation errors show problematic data fields

## Common Tasks

1. Adding new metadata fields:
   - Update parser mapping in `parsers.py`
   - Add conversion logic in `converters.py`
   - Include XML generation in `nfo_generator.py`

2. Modifying API queries:
   - Locate relevant query in `stash_api.py`
   - Follow existing GraphQL query patterns