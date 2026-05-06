# sources.py

def get_source_priority(source):
    """
    Returns the priority integer for a given D&D sourcebook.
    Lower numbers = Higher priority.
    Unknown or future books default to 99, ensuring they beat 2014-2024 era 5e books (100+).
    """
    src = str(source).upper()
    
    priorities = {
        # ==========================================
        # D&D 5.5e (2024+) & CUSTOM CORE [Priority 1-10]
        # ==========================================
        'XPHB': 1,    # Player's Handbook (2024)
        'XDMG': 2,    # Dungeon Master's Guide (2024)
        'XMM': 3,     # Monster Manual (2025)
        'FRHOF': 4,   # Forgotten Realms: Heroes of Faerun
        'EFA': 5,     # Eberron: Forge of Artifice
        
        # GAP: 11 to 99 are automatically reserved for future 5.5e books/homebrew.
        
        # ==========================================
        # D&D 5e (2014-2024) REVERSE CHRONOLOGICAL [Priority 100+]
        # ==========================================
        
        # 2024
        'QFTIS': 100, # Quests from the Infinite Staircase
        'VEOR': 101,  # Vecna: Eve of Ruin
        
        # 2023
        'BMT': 102,   # The Book of Many Things
        'PABTSO': 103,# Phandelver and Below: The Shattered Obelisk
        'PTO': 103,   # (Alternate Abbreviation)
        'GOTG': 104,  # Bigby Presents: Glory of the Giants
        'BPGOTG': 104,# (Alternate Abbreviation)
        'KFTGV': 105, # Keys from the Golden Vault
        
        # 2022
        'SOTDQ': 106, # Dragonlance: Shadow of the Dragon Queen
        'SAIS': 107,  # Spelljammer: Adventures in Space
        'AAG': 107,   # Spelljammer: Astral Adventurer's Guide (Component)
        'BAM': 107,   # Spelljammer: Boo's Astral Menagerie (Component)
        'JTTRC': 108, # Journeys through the Radiant Citadel
        'COTN': 109,  # Critical Role: Call of the Netherdeep
        'MPMM': 110,  # Mordenkainen Presents: Monsters of the Multiverse
        
        # 2021
        'SCC': 111,   # Strixhaven: A Curriculum of Chaos
        'FTOD': 112,  # Fizban's Treasury of Dragons
        'WBTW': 113,  # The Wild Beyond the Witchlight
        'VRGR': 114,  # Van Richten's Guide to Ravenloft
        'CM': 115,    # Candlekeep Mysteries
        
        # 2020
        'TCE': 116,   # Tasha's Cauldron of Everything
        'TCOE': 116,  # (Alternate Abbreviation)
        'IDROTF': 117,# Icewind Dale: Rime of the Frostmaiden
        'MOT': 118,   # Mythic Odysseys of Theros
        'EGTW': 119,  # Explorer's Guide to Wildemount
        
        # 2019
        'ERLW': 120,  # Eberron: Rising from the Last War
        'BGDIA': 121, # Baldur's Gate: Descent into Avernus
        'AI': 122,    # Acquisitions Incorporated
        'GOS': 123,   # Ghosts of Saltmarsh
        
        # 2018
        'WDMM': 124,  # Waterdeep: Dungeon of the Mad Mage
        'GGTR': 125,  # Guildmasters' Guide to Ravnica
        'WDH': 126,   # Waterdeep: Dragon Heist
        'MTF': 127,   # Mordenkainen's Tome of Foes
        'MTOF': 127,  # (Alternate Abbreviation)
        
        # 2017
        'XGE': 128,   # Xanathar's Guide to Everything
        'XGTE': 128,  # (Alternate Abbreviation)
        'TOA': 129,   # Tomb of Annihilation
        'TFTYP': 130, # Tales from the Yawning Portal
        
        # 2016
        'SKT': 131,   # Storm King's Thunder
        'VGM': 132,   # Volo's Guide to Monsters
        'VGTM': 132,  # (Alternate Abbreviation)
        'COS': 133,   # Curse of Strahd
        
        # 2015
        'SCAG': 134,  # Sword Coast Adventurer's Guide
        'OOTA': 135,  # Out of the Abyss
        'POTA': 136,  # Princes of the Apocalypse
        
        # 2014
        'DMG': 137,   # Dungeon Master's Guide (2014)
        'MM': 138,    # Monster Manual (2014)
        'ROT': 139,   # The Rise of Tiamat
        'HOTDQ': 140, # Hoard of the Dragon Queen
        'PHB': 141,   # Player's Handbook (2014)
        'LMOP': 142   # Lost Mine of Phandelver
    }
    
    return priorities.get(src, 99)