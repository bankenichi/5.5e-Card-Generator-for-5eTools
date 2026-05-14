# sources.py
import json
import os

def load_priorities():
    path = os.path.join(os.path.dirname(__file__), 'priorities.json')
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

PRIORITIES = load_priorities()

def get_source_priority(source):
    """
    Returns the priority integer for a given TTRPG sourcebook.
    Lower numbers = Higher priority.
    Unknown books default to 99.
    """
    src = str(source).upper()
    return PRIORITIES.get(src, 99)
