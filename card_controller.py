import os
import sys
import json
import webbrowser
from http.server import SimpleHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

# Import the core engine logic
from card_engine import generate_html

# ---------------------------------------------------------------------------
# CONTROLLER UI & SERVER
# ---------------------------------------------------------------------------
def get_index_html():
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Card Generator Launcher</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 2rem; background: #f4f4f4; color: #111; }
        .panel { max-width: 600px; margin: auto; padding: 1.5rem; background: white; border-radius: 12px; box-shadow: 0 8px 24px rgba(0,0,0,.08); }
        h1 { margin-top: 0; font-size: 1.6rem; }
        .dataset-group { margin-bottom: 1rem; border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden; }
        .dataset-header { background: #f9f9f9; padding: 10px 15px; display: flex; align-items: center; cursor: pointer; font-weight: bold; }
        .dataset-header input[type="checkbox"] { margin-right: 10px; transform: scale(1.2); }
        .subset-panel { display: none; padding: 10px 15px 15px 35px; border-top: 1px solid #e0e0e0; background: #fff; }
        .subset-category { margin-bottom: 10px; }
        .subset-category strong { display: block; font-size: 0.9em; margin-bottom: 5px; color: #555; }
        .filter-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); gap: 5px; }
        .filter-grid label { font-size: 0.9em; font-weight: normal; display: flex; align-items: center; cursor: pointer; }
        .filter-grid input { margin-right: 6px; }
        button { width: 100%; padding: 0.9rem 1rem; margin-top: 1rem; margin-bottom: 1rem; border: none; border-radius: 8px; font-size: 1.1rem; font-weight: bold; background: #2d7aeb; color: white; cursor: pointer; transition: background 0.2s; }
        button:hover { background: #215ec8; }
        .status { padding: 0.75rem 1rem; border-radius: 8px; background: #eef4ff; color: #0b3c79; min-height: 3rem; font-size: 0.95em; }
        a { color: #2d7aeb; font-weight: bold; }
    </style>
</head>
<body>
    <div class="panel">
        <h1>Card Generator Controller</h1>
        <p>Select datasets and apply subset filters to generate a custom printable deck.</p>
        
        <div id="datasets-container"></div>
        
        <button id="generateBtn">Generate Deck</button>
        <div id="status" class="status">Ready.</div>
    </div>

    <script>
        // Clean display names mapping (maps backend values to UI labels)
        const labelMap = {
            "0": "Cantrips",
            "A": "Abjuration",
            "C": "Conjuration",
            "D": "Divination",
            "E": "Enchantment",
            "I": "Illusion",
            "N": "Necromancy",
            "T": "Transmutation",
            "V": "Evocation",
            "str": "Strength",
            "dex": "Dexterity",
            "con": "Constitution",
            "int": "Intelligence",
            "wis": "Wisdom",
            "cha": "Charisma",
            "EI": "Eldritch Invocations",
            "AI": "Artificer Infusions",
            "AS": "Arcane Shots",
            "ED": "Elemental Disciplines",
            "FS:F": "Fighting Styles",
            "RN": "Rune Knight Runes",
            "PB": "Pact Boons",
            "MV:B": "Battle Master Maneuvers",
            "MM": "Metamagic",
            "RP": "Renown Perks",
            "none": "None / Other",
            "yes": "Requires Attunement",
            "no": "No Attunement"
        };

        const DATASETS = {
            "Actions": { file: "generators/5etools/data/actions.json", filters: {} },
            "Bastions": { file: "generators/5etools/data/bastions.json", filters: { level: ["5", "9", "13", "17"] } },
            "Classes": { 
                file: ["generators/5etools/data/class/index.json", "generators/5etools/data/optionalfeatures.json"], 
                filters: {
                    name: ["Artificer", "Barbarian", "Bard", "Cleric", "Druid", "Fighter", "Monk", "Paladin", "Ranger", "Rogue", "Sorcerer", "Warlock", "Wizard"],
                    archetype: ["Spellcaster", "Half-Caster", "Martial", "Gish / Subclass Caster"]
                } 
            },
            "Conditions / Diseases": { file: "generators/5etools/data/conditionsdiseases.json", filters: {} },
            "Decks": { file: "generators/5etools/data/decks.json", filters: {} },
            "Deities": { 
                file: "generators/5etools/data/deities.json", 
                filters: { 
                    pantheon: [
                        "Celtic", "Dawn War", "Dragonlance", "Drow", "Duergar", "Dwarven", 
                        "Eberron", "Egyptian", "Elven", "Exandria", "Faerûnian", "Forgotten Realms", 
                        "Gnome", "Gnomish", "Greek", "Greyhawk", "Halfling", "Nonhuman", 
                        "Norse", "Orc", "Theros", "Yuan-ti"
                    ] 
                } 
            },
            "Feats": { 
                file: "generators/5etools/data/feats.json", 
                filters: { category: ["General Feat", "Origin Feat", "Epic Boon", "Fighting Style"] } 
            },
            "Items": { file: "generators/5etools/data/items.json", filters: { rarity: ["common", "uncommon", "rare", "very rare", "legendary", "artifact", "none"], attunement: ["yes", "no"] } },
            "Languages": { 
                file: "generators/5etools/data/languages.json", 
                filters: { type: ["Standard", "Rare"] } // Added normalized filters
            },
            "Optional Features": { 
                file: "generators/5etools/data/optionalfeatures.json", 
                subtitle: "(Invocations, Infusions, Maneuvers, Fighting Styles, etc.)",
                filters: { featureType: ["EI", "AI", "AS", "ED", "FS:F", "RN", "PB", "MV:B", "MM", "RP"] } 
            },
            "Psionics": { file: "generators/5etools/data/psionics.json", filters: {} },
            "Races": { file: "generators/5etools/data/races.json", filters: {} },
            "Skills": { file: "generators/5etools/data/skills.json", filters: { ability: ["str", "dex", "con", "int", "wis", "cha"] } },
            "Spells": { file: "generators/5etools/data/spells/index.json", filters: { level: ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"], school: ["A", "C", "D", "E", "I", "N", "T", "V"] } },
            "Vehicles": { file: "generators/5etools/data/vehicles.json", filters: {} }
        };

        const container = document.getElementById('datasets-container');

        // Render UI
        Object.entries(DATASETS).forEach(([name, data]) => {
            const group = document.createElement('div');
            group.className = 'dataset-group';

            const header = document.createElement('div');
            header.className = 'dataset-header';
            
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.id = `ds-${name}`;
            checkbox.value = name;
            
            const label = document.createElement('label');
            label.htmlFor = `ds-${name}`;
            label.style.display = 'flex';
            label.style.flexDirection = 'column';
            label.style.margin = "0";
            label.style.cursor = "pointer";
            label.style.flexGrow = "1";

            const titleSpan = document.createElement('span');
            titleSpan.innerText = name;
            label.appendChild(titleSpan);

            // Add the subtitle below the main label if it exists
            if (data.subtitle) {
                const subSpan = document.createElement('span');
                subSpan.innerText = data.subtitle;
                subSpan.style.fontSize = "0.75em";
                subSpan.style.color = "#666";
                subSpan.style.fontWeight = "normal";
                subSpan.style.marginTop = "2px";
                label.appendChild(subSpan);
            }

            header.appendChild(checkbox);
            header.appendChild(label);
            group.appendChild(header);

            const subsetPanel = document.createElement('div');
            subsetPanel.className = 'subset-panel';
            subsetPanel.id = `panel-${name}`;

            if (Object.keys(data.filters).length > 0) {
                Object.entries(data.filters).forEach(([filterKey, filterValues]) => {
                    const catDiv = document.createElement('div');
                    catDiv.className = 'subset-category';
                    catDiv.innerHTML = `<strong>Filter by ${filterKey.charAt(0).toUpperCase() + filterKey.slice(1)}:</strong>`;
                    
                    const grid = document.createElement('div');
                    grid.className = 'filter-grid';

                    filterValues.forEach(val => {
                        const lbl = document.createElement('label');
                        const chk = document.createElement('input');
                        chk.type = 'checkbox';
                        chk.value = val;
                        chk.dataset.filterKey = filterKey;
                        chk.dataset.datasetName = name;
                        
                        // Map the value to a clean label, or fallback to capitalized default
                        let displayLabel = labelMap[val] || (val.charAt(0).toUpperCase() + val.slice(1));
                        
                        lbl.appendChild(chk);
                        lbl.appendChild(document.createTextNode(" " + displayLabel));
                        grid.appendChild(lbl);
                    });
                    
                    catDiv.appendChild(grid);
                    subsetPanel.appendChild(catDiv);
                });
            } else {
                subsetPanel.innerHTML = '<span style="color:#888; font-size:0.9em;">No subset filters available for this dataset.</span>';
            }
            
            group.appendChild(subsetPanel);
            container.appendChild(group);

            // Toggle logic
            checkbox.addEventListener('change', (e) => {
                subsetPanel.style.display = e.target.checked ? 'block' : 'none';
            });
        });

        // Submit logic
        const status = document.getElementById('status');
        document.getElementById('generateBtn').addEventListener('click', async () => {
            const payload = { datasets: [] };
            
            document.querySelectorAll('.dataset-header input[type="checkbox"]:checked').forEach(cb => {
                const name = cb.value;
                const file = DATASETS[name].file;
                const filterInputs = document.querySelectorAll(`input[data-dataset-name="${name}"]:checked`);
                
                const filters = {};
                filterInputs.forEach(input => {
                    const key = input.dataset.filterKey;
                    if (!filters[key]) filters[key] = [];
                    filters[key].push(input.value);
                });

                payload.datasets.push({ name, file, filters });
            });

            if (payload.datasets.length === 0) {
                status.textContent = 'Please select at least one dataset.';
                return;
            }

            status.textContent = 'Generating custom deck...';
            try {
                const response = await fetch('/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                status.innerHTML = await response.text();
            } catch (error) {
                status.textContent = 'Error: ' + error;
            }
        });
    </script>
</body>
</html>"""

class GeneratorRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == '/': 
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(get_index_html().encode('utf-8'))
            return
        super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == '/generate':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                payload = json.loads(post_data.decode('utf-8'))
                output_filename = "Custom_Deck_Cards.html"
                
                result = generate_html(payload, output_html_path=output_filename)
                
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.end_headers()
                
                if result and isinstance(result, dict) and result.get("card_count", 0) > 0: 
                    cc = result["card_count"]
                    ic = result["item_count"]
                    tc = result["type_counts"]
                    
                    # Sort types by count descending for a clean UI
                    sorted_tc = sorted(tc.items(), key=lambda item: item[1], reverse=True)
                    badges = "".join([f'<span style="display: inline-block; background: #d0def4; color: #0b3c79; padding: 3px 8px; border-radius: 12px; font-size: 0.8em; margin: 0 4px 4px 0;"><strong>{k}:</strong> {v}</span>' for k, v in sorted_tc])
                    
                    html_resp = f'''
                    <div style="margin-bottom: 10px;">
                        <span style="font-size: 1.1em; color: #111;">Success! Generated a deck of <strong>{cc}</strong> cards from <strong>{ic}</strong> unique items.</span>
                    </div>
                    <div style="margin-bottom: 15px;">
                        {badges}
                    </div>
                    <p><a href="/{output_filename}" target="_blank" style="text-decoration: none; font-weight: bold; background: #2d7aeb; color: #fff; padding: 8px 16px; border-radius: 6px;">Open Custom Deck</a></p>
                    '''
                    self.wfile.write(html_resp.encode('utf-8'))
                else: 
                    self.wfile.write(b'<p style="color: #d32f2f;">No cards matched your filter criteria.</p>')
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f'Server Error: {str(e)}'.encode('utf-8'))
            return

def serve_gui(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, GeneratorRequestHandler)
    url = f'http://localhost:{port}/'
    print(f'Serving card generator UI at {url}')
    webbrowser.open(url)
    try: 
        httpd.serve_forever()
    except KeyboardInterrupt: 
        print('\nServer stopped.')
        httpd.server_close()

if __name__ == '__main__':
    serve_gui()