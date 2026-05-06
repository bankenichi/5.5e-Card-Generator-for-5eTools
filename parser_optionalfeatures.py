import copy

FEATURE_TYPE_MAP = {
    "EI": "Eldritch Invocation",
    "AI": "Artificer Infusion",
    "MV:B": "Maneuver",
    "AS": "Arcane Shot",
    "FS:F": "Fighting Style",
    "FS:R": "Fighting Style",
    "FS:P": "Fighting Style",
    "FS:B": "Fighting Style",
    "ED": "Elemental Discipline",
    "RN": "Rune",
    "RP": "Renown Perk",
    "PB": "Pact Boon",
    "MM": "Metamagic" # Added Metamagic mapping
}

def format_prerequisite(prereq):
    """Translates complex prerequisite dictionaries into human-readable strings."""
    parts = []
    if "level" in prereq:
        lvl = prereq["level"]
        if isinstance(lvl, dict):
            parts.append(f"Level {lvl.get('level')} {lvl.get('class', {}).get('name', '')}")
        else:
            parts.append(f"Level {lvl}")
    if "pact" in prereq:
        parts.append(f"Pact of the {prereq['pact']}")
    if "spell" in prereq:
        spells = [s.split('|')[0].replace('#c', '') for s in prereq["spell"] if isinstance(s, str)]
        if spells: parts.append(f"Spell: {', '.join(spells)}")
    if "item" in prereq:
        parts.append(f"Item: {', '.join(prereq['item'])}")
    if "otherSummary" in prereq:
        parts.append(prereq["otherSummary"].get("entrySummary", ""))
    
    return "; ".join(p for p in parts if p)

def enrich_optional_feature(item, type_map=None):
    result = copy.deepcopy(item)
    
    # 1. Determine Meta Label
    f_types = result.get('featureType', [])
    meta = "Optional Feature"
    for ft in f_types:
        if ft in FEATURE_TYPE_MAP:
            meta = FEATURE_TYPE_MAP[ft]
            break
    
    # 2. Process Prerequisites into the top of entries
    prereqs = result.get('prerequisite', [])
    if prereqs:
        prereq_str = ", ".join(format_prerequisite(p) for p in prereqs)
        if prereq_str:
            result['entries'].insert(0, f"<i>Prerequisite: {prereq_str}</i>")

    result['meta_left'] = meta
    result['_data_type'] = "optionalfeature"
    return result