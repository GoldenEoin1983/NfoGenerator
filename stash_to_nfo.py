#!/usr/bin/env python3
"""
StashApp to NFO Converter
Converts StashApp JSON metadata files into Kodi/Jellyfin compatible NFO files.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Optional

from parsers import StashParser
from converters import StashToNfoConverter
from nfo_generator import NfoGenerator
from stash_api import StashApiClient


def main():
    """Main entry point for the StashApp to NFO converter."""
    parser = argparse.ArgumentParser(
        description="Convert StashApp JSON metadata files to Kodi/Jellyfin NFO format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s scene.json scene.nfo
  %(prog)s --type performer performer.json performer.nfo
  %(prog)s --type gallery gallery.json gallery.nfo
        """
    )
    
    # Create mutually exclusive group for input methods
    input_group = parser.add_mutually_exclusive_group(required=True)
    
    input_group.add_argument(
        "input_file",
        nargs="?",
        help="Path to the StashApp JSON file"
    )
    
    input_group.add_argument(
        "--stash-id",
        type=int,
        help="Query StashApp directly by scene/performer/gallery ID"
    )
    
    input_group.add_argument(
        "--search",
        help="Search StashApp by query string and convert first result"
    )
    
    parser.add_argument(
        "output_file", 
        nargs="?",
        help="Path for the output NFO file (optional, auto-generated based on input)"
    )
    
    parser.add_argument(
        "--type",
        choices=["scene", "performer", "gallery", "auto"],
        default="auto",
        help="Type of StashApp data to convert (default: auto-detect)"
    )
    
    parser.add_argument(
        "--encoding",
        default="utf-8",
        help="Output file encoding (default: utf-8)"
    )
    
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print the XML output with indentation"
    )
    
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing output files without prompting"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--extract-images",
        action="store_true",
        help="Extract and save base64 encoded images alongside NFO file"
    )
    
    # StashApp API connection options
    api_group = parser.add_argument_group("StashApp API Options", "Configure connection to local StashApp instance")
    
    api_group.add_argument(
        "--stash-host",
        default="localhost",
        help="StashApp server hostname (default: localhost)"
    )
    
    api_group.add_argument(
        "--stash-port",
        default="9999", 
        help="StashApp server port (default: 9999)"
    )
    
    api_group.add_argument(
        "--stash-scheme",
        choices=["http", "https"],
        default="http",
        help="StashApp connection scheme (default: http)"
    )
    
    api_group.add_argument(
        "--stash-api-key",
        help="StashApp API key for authentication"
    )
    
    api_group.add_argument(
        "--stash-username",
        help="StashApp username (alternative to API key)"
    )
    
    api_group.add_argument(
        "--stash-password",
        help="StashApp password (use with username)"
    )
    
    args = parser.parse_args()
    
    # Validate input arguments
    if not any([args.input_file, args.stash_id, args.search]):
        print("Error: Must specify either input_file, --stash-id, or --search", file=sys.stderr)
        sys.exit(1)
    
    # Initialize variables
    stash_data = None
    data_source = None
    output_path = None
    
    # Handle different input methods
    if args.input_file:
        # File-based input (original method)
        input_path = Path(args.input_file)
        if not input_path.exists():
            print(f"Error: Input file '{args.input_file}' does not exist.", file=sys.stderr)
            sys.exit(1)
        
        if not input_path.is_file():
            print(f"Error: '{args.input_file}' is not a file.", file=sys.stderr)
            sys.exit(1)
        
        data_source = str(input_path)
        
        # Determine output file path
        if args.output_file:
            output_path = Path(args.output_file)
        else:
            output_path = input_path.with_suffix('.nfo')
    
    elif args.stash_id or args.search:
        # API-based input
        try:
            # Create API client
            if args.verbose:
                print(f"Connecting to StashApp at {args.stash_scheme}://{args.stash_host}:{args.stash_port}")
            
            stash_client = StashApiClient(
                host=args.stash_host,
                port=args.stash_port, 
                scheme=args.stash_scheme,
                api_key=args.stash_api_key,
                username=args.stash_username,
                password=args.stash_password
            )
            
            if args.verbose:
                conn_info = stash_client.get_connection_info()
                auth_status = "authenticated" if conn_info["authenticated"] else "no authentication"
                print(f"Connected to StashApp ({auth_status})")
            
            # Fetch data based on method
            if args.stash_id:
                # Direct ID lookup
                stash_id = args.stash_id
                data_source = f"StashApp ID {stash_id}"
                
                if args.verbose:
                    print(f"Fetching data for ID {stash_id}")
                
                # Try to determine type and fetch appropriate data
                data_type = args.type if args.type != "auto" else None
                
                if data_type == "scene" or data_type is None:
                    try:
                        stash_data = stash_client.get_scene(stash_id)
                        data_type = "scene"
                    except Exception as e:
                        if data_type == "scene":
                            print(f"Error: {e}", file=sys.stderr)
                            sys.exit(1)
                
                if (data_type == "performer" or data_type is None) and not stash_data:
                    try:
                        stash_data = stash_client.get_performer(stash_id)
                        data_type = "performer"
                    except Exception as e:
                        if data_type == "performer":
                            print(f"Error: {e}", file=sys.stderr)
                            sys.exit(1)
                
                if (data_type == "gallery" or data_type is None) and not stash_data:
                    try:
                        stash_data = stash_client.get_gallery(stash_id)
                        data_type = "gallery"
                    except Exception as e:
                        if data_type == "gallery":
                            print(f"Error: {e}", file=sys.stderr)
                            sys.exit(1)
                
                if not stash_data:
                    print(f"Error: Could not find any data with ID {stash_id} (tried scene, performer, gallery)", file=sys.stderr)
                    sys.exit(1)
                
                # Override type detection
                args.type = data_type
            
            elif args.search:
                # Search-based lookup
                search_query = args.search
                data_source = f"StashApp search '{search_query}'"
                
                if args.verbose:
                    print(f"Searching for '{search_query}'")
                
                # Search scenes (most common use case)
                results = stash_client.search_scenes(search_query, limit=1)
                if not results:
                    print(f"Error: No scenes found for search query '{search_query}'", file=sys.stderr)
                    sys.exit(1)
                
                # Get full data for first result
                scene_id = int(results[0]["id"])
                stash_data = stash_client.get_scene(scene_id)
                args.type = "scene"  # Override type since we searched scenes
                
                if args.verbose:
                    print(f"Found scene: {stash_data.get('title', 'Unknown Title')} (ID: {scene_id})")
            
            # Determine output file path for API data
            if args.output_file:
                output_path = Path(args.output_file)
            else:
                # Generate filename based on data
                title = stash_data.get('title', f"stash_{args.stash_id or 'search'}")
                # Sanitize filename
                safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
                safe_title = safe_title.replace(" ", "_")
                output_path = Path(f"{safe_title}.nfo")
        
        except Exception as e:
            print(f"Error connecting to StashApp: {e}", file=sys.stderr)
            sys.exit(1)
    
    # Check if output file exists and handle overwrite
    if output_path.exists() and not args.overwrite:
        response = input(f"Output file '{output_path}' already exists. Overwrite? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            print("Operation cancelled.")
            sys.exit(0)
    
    try:
        # Parse data (either from file or API)
        if args.input_file:
            # File-based parsing
            if args.verbose:
                print(f"Reading input file: {input_path}")
            
            parser_instance = StashParser()
            stash_data = parser_instance.parse_file(input_path)
        
        # If we got data from API, stash_data is already set
        if args.verbose:
            print(f"Processing data from: {data_source}")
        
        # Auto-detect type if not specified
        data_type = args.type
        if data_type == "auto":
            data_type = parser_instance.detect_type(stash_data)
            if args.verbose:
                print(f"Auto-detected type: {data_type}")
        
        # Convert to NFO format
        if args.verbose:
            print(f"Converting {data_type} data to NFO format")
        
        converter = StashToNfoConverter()
        nfo_data = converter.convert(stash_data, data_type)
        
        # Generate NFO XML
        if args.verbose:
            print(f"Generating NFO XML")
        
        generator = NfoGenerator(encoding=args.encoding, pretty_print=args.pretty)
        nfo_xml = generator.generate(nfo_data, data_type)
        
        # Extract images if requested
        extracted_images = []
        if args.extract_images:
            if args.verbose:
                print(f"Extracting base64 encoded images")
            
            extracted_images = converter.extract_images(stash_data, output_path)
            if extracted_images:
                if args.verbose:
                    print(f"Extracted {len(extracted_images)} images: {', '.join(extracted_images)}")
            elif args.verbose:
                print("No base64 encoded images found to extract")
        
        # Write output file
        if args.verbose:
            print(f"Writing output file: {output_path}")
        
        with open(output_path, 'w', encoding=args.encoding) as f:
            f.write(nfo_xml)
        
        print(f"Successfully converted '{data_source}' to '{output_path}'")
        
        if extracted_images:
            print(f"Extracted {len(extracted_images)} images: {', '.join(extracted_images)}")
        
        if args.verbose:
            print(f"Output file size: {output_path.stat().st_size} bytes")
    
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in input file: {e}", file=sys.stderr)
        sys.exit(1)
    
    except FileNotFoundError as e:
        print(f"Error: File not found: {e}", file=sys.stderr)
        sys.exit(1)
    
    except PermissionError as e:
        print(f"Error: Permission denied: {e}", file=sys.stderr)
        sys.exit(1)
    
    except Exception as e:
        print(f"Error: Unexpected error occurred: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
