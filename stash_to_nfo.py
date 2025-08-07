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
    
    parser.add_argument(
        "input_file",
        help="Path to the StashApp JSON file"
    )
    
    parser.add_argument(
        "output_file", 
        nargs="?",
        help="Path for the output NFO file (optional, defaults to input filename with .nfo extension)"
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
    
    args = parser.parse_args()
    
    # Validate input file
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: Input file '{args.input_file}' does not exist.", file=sys.stderr)
        sys.exit(1)
    
    if not input_path.is_file():
        print(f"Error: '{args.input_file}' is not a file.", file=sys.stderr)
        sys.exit(1)
    
    # Determine output file path
    if args.output_file:
        output_path = Path(args.output_file)
    else:
        output_path = input_path.with_suffix('.nfo')
    
    # Check if output file exists and handle overwrite
    if output_path.exists() and not args.overwrite:
        response = input(f"Output file '{output_path}' already exists. Overwrite? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            print("Operation cancelled.")
            sys.exit(0)
    
    try:
        # Parse the StashApp JSON file
        if args.verbose:
            print(f"Reading input file: {input_path}")
        
        parser_instance = StashParser()
        stash_data = parser_instance.parse_file(input_path)
        
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
        
        # Write output file
        if args.verbose:
            print(f"Writing output file: {output_path}")
        
        with open(output_path, 'w', encoding=args.encoding) as f:
            f.write(nfo_xml)
        
        print(f"Successfully converted '{input_path}' to '{output_path}'")
        
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
