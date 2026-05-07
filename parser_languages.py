import copy
from parser_utils import (
    BYPASS_EXCLUDED_SOURCES_DTYPES,
    SOURCE_PRIORITY_OVERRIDES,
    NORMALIZE_TYPE_HOOKS,
)

# ---------------------------------------------------------------------------
# LANGUAGE-SPECIFIC TYPE NORMALIZATION
# Maps raw 5etools type values to the two canonical display values used by
# the filter UI.  Registered into NORMALIZE_TYPE_HOOKS so normalize_item
# in card_engine.py never needs to know about this.
# ---------------------------------------------------------------------------
_LANGUAGE_TYPE_MAP = {
    'standard': 'Standard',
    'exotic':   'Rare',
    'rare':     'Rare',
    'secret':   'Rare',   # Druidic, Thieves' Cant — classified as Rare
    '':         'Standard',
}

def _normalize_language_type(item: dict) -> str:
    raw = str(item.get('type', '') or '').lower().strip()
    return _LANGUAGE_TYPE_MAP.get(raw, 'Standard')

# Register for both singular and plural dtype keys.
for _dt in ('language', 'languages'):
    NORMALIZE_TYPE_HOOKS[_dt] = _normalize_language_type

# ---------------------------------------------------------------------------
# SCAG SOURCE PRIORITY OVERRIDE
# SCAG is always preferred for languages because it carries regional dialect
# data that newer printings omit.  Priority 0 beats every other source.
# ---------------------------------------------------------------------------
def _language_source_priority(source: str):
    if str(source).upper() == 'SCAG':
        return 0
    return None  # fall through to global get_source_priority()

for _dt in ('language', 'languages'):
    SOURCE_PRIORITY_OVERRIDES[_dt] = _language_source_priority

# ---------------------------------------------------------------------------
# BYPASS EXCLUDED SOURCES
# Languages should always pass through even if their source is in the global
# EXCLUDED_SOURCES set.
# ---------------------------------------------------------------------------
BYPASS_EXCLUDED_SOURCES_DTYPES.update({'language', 'languages'})


# ---------------------------------------------------------------------------
# ENRICHMENT
# ---------------------------------------------------------------------------
def enrich_language(item, type_map=None):
    """
    Specific parsing and enrichment for Languages with 5.5e color schemes.
    """
    result = copy.deepcopy(item)
    
    # 1. Normalize Category and Assign Colors
    #    _normalize_language_type is already called by normalize_item via the
    #    NORMALIZE_TYPE_HOOKS registry, so result['type'] is already canonical
    #    ('Standard' or 'Rare') by the time we arrive here.
    canonical_type = str(result.get('type', 'Standard'))

    if canonical_type == 'Rare':
        pc = "#795548"  # Rich Bronze/Brown
        bc = "#EFEBE9"  # Light Parchment
    else:
        pc = "#455A64"  # Steel Blue/Grey
        bc = "#ECEFF1"  # Very Light Blue-Grey

    result['meta_left'] = canonical_type
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
