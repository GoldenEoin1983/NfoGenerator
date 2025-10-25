# Copilot instructions — NfoGenerator (concise)

Purpose: Convert StashApp JSON (scenes, performers, galleries) into Kodi/Jellyfin NFO XML.

High-level architecture (why):
- CLI: `stash_to_nfo.py` orchestrates input selection (file / --stash-id / --search), validation, and output.
- Parsing: `parsers.py` reads JSON and detects type (scene/performer/gallery).
- Conversion: `converters.py` maps StashApp shapes → NFO data model (actors, genres, uniqueid, runtime).
- XML: `nfo_generator.py` turns converted dicts into ElementTree XML (movie/actor NFOs).
- API: `stash_api.py` wraps `stashapp-tools` (GraphQL) for direct retrieval when using `--stash-id`/`--search`.

Key files (quick lookup):
- `stash_to_nfo.py` — CLI and main flow (see CLI flags like `--pretty`, `--extract-images`, `--verbose`).
- `parsers.py` — `StashParser.parse_file()` and `detect_type()` (auto-detect logic used by CLI).
- `converters.py` — `StashToNfoConverter.convert()`; contains `_convert_scene`, `_convert_performer`, `_convert_gallery` and image extraction helpers.
- `nfo_generator.py` — `NfoGenerator.generate()` producing either movie or actor NFOs using ElementTree + minidom for pretty print.
- `stash_api.py` — `StashApiClient` uses `stashapp-tools` (`StashInterface`) and contains example GraphQL queries (gallery/search helpers).

Developer workflows (how to run locally):
- Requires Python >= 3.11 (see `pyproject.toml`) and dependency `stashapp-tools>=0.2.58`.
- Quick examples:
  - File: `python stash_to_nfo.py scene.json`
  - API by ID: `python stash_to_nfo.py --stash-id 123`
  - Search: `python stash_to_nfo.py --search "query"`
- For debugging connections: use `--verbose` to print connection/info and stack traces.

Project-specific conventions & patterns:
- Data flow is linear: parse → convert → generate. Add fields by updating exactly these three layers.
- Converters produce a plain dict shaped for `NfoGenerator` (not XML strings). Keep converter outputs simple and serializable.
- Image extraction: `StashToNfoConverter.extract_images()` decodes base64 fields (`cover`, `poster`, `thumbnail`, `fanart`) and writes files next to the NFO.
- Filename sanitization and output path generation live in `stash_to_nfo.py` when input is from API.

Integration points & gotchas:
- `stash_api.py` calls `StashInterface` from `stashapp-tools` — network errors are raised as ConnectionError/RuntimeError; CLI handles them and exits.
- Gallery queries use raw GraphQL in `stash_api.py` (example query present) — modify there when adding new fields to fetch.
- XML: ElementTree + minidom; NFO files must be UTF-8 and include the XML declaration (see `_format_xml`).

If you need to add a metadata field (concrete steps):
1. Update parser (if field comes from JSON) in `parsers.py` or accept it via API client.
2. Map it in `converters.py` into the NFO dict (follow naming used by `nfo_generator.py`).
3. Add XML emission in `nfo_generator.py` if a new tag or structure is required.

Useful examples & test assets: check `attached_assets/` for sample `.json` and `.nfo` outputs to mirror formatting.

Questions? If anything above is ambiguous, tell me which file or workflow you want expanded and I will iterate.

Developer quickstart (venv, deps, run)
- Create and activate a local venv, install the runtime dependency used here (`stashapp-tools`):

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install "stashapp-tools>=0.2.58"
```

- Run the converter on an example file (attached assets include sample JSON/NFO):

```bash
python stash_to_nfo.py attached_assets/Chef-At-Home.90b733be224204c1_1754551910073.json --pretty
python stash_to_nfo.py --stash-id 123 --verbose  # API example (needs StashApp credentials/host)
```

GraphQL queries (examples & editing advice)
-- The project uses `stashapp-tools` (`StashInterface`) in `stash_api.py`. Two representative queries are embedded and used when the library doesn't provide a helper.
-- Copy/paste and edit these when you need extra fields. Keep the same variable structure and return shape to avoid breaking the caller code.

Gallery query (from `StashApiClient.get_gallery`):

```graphql
query FindGallery($id: ID!) {
  findGallery(id: $id) {
    id
    title
    url
    date
    details
    rating
    organized
    studio {
      name
    }
    performers {
      name
    }
    tags {
      name
    }
    scenes {
      id
      title
    }
    folder {
      path
    }
    images {
      path
    }
    cover
    created_at
    updated_at
  }
}
```

Scene search query (used by `search_scenes`):

```graphql
query FindScenes($filter: FindFilterType, $scene_filter: SceneFilterType) {
  findScenes(filter: $filter, scene_filter: $scene_filter) {
    scenes {
      id
      title
      studio {
        name
      }
      performers {
        name
      }
      files {
        path
      }
    }
  }
}
```

Find-by-path query (used by `find_scene_by_path`):

```graphql
query FindScenes($filter: FindFilterType, $scene_filter: SceneFilterType) {
  findScenes(filter: $filter, scene_filter: $scene_filter) {
    scenes {
      id
      title
      files {
        path
      }
    }
  }
}
```

Editing advice:
- Add fields under the object you need (e.g., add `studio { id name }` to fetch studio id). Keep nesting shallow for performance.
- Use variables (the code passes `variables` dict) — avoid hardcoding IDs in the query string.
- When adding fields check the resulting JSON keys used by `converters.py` and `parsers.py` and update them accordingly (mapping must match).
- If you add large data (e.g., image blobs), prefer to request only metadata and use the file/image endpoints or `cover` fields already present.

If you'd like, I can add a tiny example PR that adds a new field end-to-end (parser → converter → generator) so you can see the exact edits required.