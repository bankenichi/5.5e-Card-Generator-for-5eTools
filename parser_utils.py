import re

def clean_tags(text):
    text = str(text)
    LAST_PART_TAGS = {'adventure', 'homebrew'}
    DROP_TAGS = {'note', '5etools', 'quickref'}
    TITLE_TAGS = {'spell', 'item', 'condition', 'disease', 'background', 'race', 'optfeature', 'class', 'subclass', 'deity'}

    def replace_tag(match):
        tag_name = match.group(1).lower()
        inner = (match.group(2) or "").strip()
        parts = [p.strip() for p in inner.split('|')]

        if tag_name == 'card':
            if len(parts) > 3 and parts[3]:
                return parts[3]
            return parts[0]

        if tag_name == 'atk':
            atk_map = {
                'm': 'Melee Attack:', 'r': 'Ranged Attack:',
                'mw': 'Melee Weapon Attack:', 'rw': 'Ranged Weapon Attack:',
                'ms': 'Melee Spell Attack:', 'rs': 'Ranged Spell Attack:',
                'mw,rw': 'Melee or Ranged Weapon Attack:',
                'ms,rs': 'Melee or Ranged Spell Attack:',
                'g': ''
            }
            val = atk_map.get(parts[0].replace(' ', '').lower(), '')
            return f"<i>{val}</i>" if val else ""

        if tag_name == 'hit':
            val = parts[0]
            if val and not val.startswith(('+', '-')): return f"+{val}"
            return val

        if tag_name == 'h':
            return "<i>Hit:</i>"

        if tag_name == 'recharge':
            return f"(Recharge {parts[0]}-6)" if parts and parts[0] else "(Recharge)"

        if tag_name == 'dc':
            return f"DC {parts[0]}"

        if tag_name == 'filter':
            return parts[0] if parts else ""

        if tag_name in DROP_TAGS:
            return re.sub(r'@\w+\s*', '', inner).split('|')[0].strip()

        if tag_name in TITLE_TAGS:
            val = parts[0] if parts else ""
            return val.title()

        if tag_name == 'book':
            book_name = parts[0] if len(parts) > 0 else ""
            chapter = parts[2] if len(parts) > 2 and parts[2] else ""
            section = parts[3] if len(parts) > 3 and parts[3] else ""
            res = book_name
            if chapter: res += f", Chapter {chapter}"
            if section: res += f" ({section})"
            return res

        if tag_name in LAST_PART_TAGS:
            for p in reversed(parts):
                if p: return p
            return parts[0] if parts else ""

        if tag_name == 'link':
            return parts[0] if parts else ""

        if len(parts) > 2 and parts[2]:
            return parts[2]
        return parts[0] if parts else ""

    for _ in range(10):
        new_text = re.sub(r"\{[@#](\w+)(?:\s+([^{}]+))?\}", replace_tag, text)
        if new_text == text:
            break
        text = new_text

    text = re.sub(r"\{[^}]*\}", "", text)
    text = re.sub(r"@\w+\s*", "", text)
    text = text.replace("}", "").replace("{", "")
    text = re.sub(r"(?i)\* This generic variant has the same name and source as the item .*?(?:\.|$)", "", text)
    return text.strip()

def tokenize_text(text):
    return re.findall(r'\{@[^}]+\}|\S+', text)


# ---------------------------------------------------------------------------
# ENGINE HOOK REGISTRIES
#
# Parsers self-register into these dicts at import time.  The engine reads
# them without needing to know which dtypes exist.
# ---------------------------------------------------------------------------

# BYPASS_EXCLUDED_SOURCES_DTYPES
# Set of _data_type strings whose items are never dropped by the global
# EXCLUDED_SOURCES filter (e.g. 'deity', 'class', 'background' ...).
# Parsers add their dtype strings here at module level.
BYPASS_EXCLUDED_SOURCES_DTYPES: set = set()

# SOURCE_PRIORITY_OVERRIDES
# dtype -> callable(source: str) -> int | None
# If the callable returns a non-None int, that value replaces the default
# get_source_priority() result for items of that dtype.
# Returning None falls through to the global priority function.
SOURCE_PRIORITY_OVERRIDES: dict = {}

# PRE_FILTER_HOOKS
# dtype -> callable(norm_item: dict, primary_file: str, all_raw: list) -> None
# Called once per deduplicated item before the filter pass.
# Mutates norm_item in-place to inject dtype-specific filterable fields
# (e.g. 'pantheon' for deities, 'classes' for spells, 'archetype' for classes).
PRE_FILTER_HOOKS: dict = {}

# NORMALIZE_TYPE_HOOKS
# dtype -> callable(item: dict) -> str
# Called inside normalize_item to produce the canonical 'type' string for
# items of that dtype.  Returning '' falls back to the raw item['type'] value.
NORMALIZE_TYPE_HOOKS: dict = {}

# FOOTER_RENDERERS
# dtype -> callable(item: dict) -> (cost_str: str, weight_str: str)
# Called during HTML rendering to produce the bottom footer row for an item.
# Returns a (cost_str, weight_str) tuple of already-formatted strings.
# The sentinel key '_items' is used as the universal fallback for item-type
# data that has no more-specific registration.
FOOTER_RENDERERS: dict = {}

# META_ONLY_DTYPES
# Set of _data_type strings that are purely reference/lookup data and must
# never be rendered as cards.  Parsers add their meta dtypes here at module level.
META_ONLY_DTYPES: set = {
    'itemType', 'itemProperty', 'itemTypeAdditionalEntries', 'itemEntry',
    'classFeature', 'subclassFeature',
}
