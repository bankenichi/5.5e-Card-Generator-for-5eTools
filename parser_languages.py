import copy

def enrich_language(item, type_map=None):
    """
    Specific parsing and enrichment for Languages with 5.5e color schemes.
    """
    result = copy.deepcopy(item)
    
    # 1. Normalize Category and Assign Colors
    raw_type = str(result.get('type', '')).strip().lower()
    
    if raw_type in ('exotic', 'rare'):
        meta = "Rare"
        pc = "#795548"  # Rich Bronze/Brown
        bc = "#EFEBE9"  # Light Parchment
    else:
        # Default for 'standard', 'language', or missing
        meta = "Standard"
        pc = "#455A64"  # Steel Blue/Grey
        bc = "#ECEFF1"  # Very Light Blue-Grey
        
    result['meta_left'] = meta
    result['type'] = meta  # Normalize for UI filtering
    result['primary_color'] = pc
    result['bg_color'] = bc
    
    # 2. Extract specific metadata
    stats = []
    script = result.get('script')
    if script:
        stats.append({'type': 'item', 'name': 'Script', 'entry': str(script).title()})
        
    speakers = result.get('typicalSpeakers')
    if speakers:
        stats.append({'type': 'item', 'name': 'Typical Speakers', 'entry': ", ".join(str(s) for s in speakers)})

    origin = result.get('origin')
    if origin:
        stats.append({'type': 'item', 'name': 'Origin', 'entry': str(origin)})

    # 3. Clean entries (Remove SCAG variant rules block)
    current_entries = result.get('entries', [])
    if not isinstance(current_entries, list):
        current_entries = [current_entries]
        
    cleaned_entries = [e for e in current_entries if not (isinstance(e, dict) and e.get('name') == 'Option: Human Languages')]
    result['entries'] = stats + cleaned_entries
    result['_data_type'] = "language"
    
    return result