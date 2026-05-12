# 5.5e Card Generator for 5eTools

A fully local tool that connects to the 5etools dataset to generate custom, printable reference cards for your Dungeons & Dragons games. 

Whether you need spell cards, item cards, class features, or bastion rules, this generator pulls the most up-to-date information and automatically formats it into clean, readable cards ready for the table (allegedly).

| **Category** | **Number of Cards** | **Unique Entries** |
| :--- | ---: | ---: |
| Actions | 35 | 34 |
| Backgrounds | 306 | 146 |
| Bastions | 58 | 53 |
| Bestiary | 4707 | 3720 |
| Classes | 626 | 383 |
| Conditions | 44 | 44 |
| Decks | 375 | 369 |
| Deities | 464 | 322 |
| Feats | 218 | 218 |
| Items | 2141 | 1983 |
| Languages | 110 | 110 |
| Optional Features | 159 | 157 |
| Psionics | 49 | 49 |
| Races | 196 | 175 |
| Skills | 18 | 18 |
| Spells | 570 | 553 |
| Vehicles | 77 | 69 |
| **Total** | **10153** | **8403** |

##  Features

* **5.5e Smart Prioritization:** Built with the 2024 rules update in mind. If an item, spell, or feature exists in multiple books, the engine automatically prioritizes the newest 2024 core rulebooks (e.g., XPHB, XDMG, XMM) over the legacy 2014 versions.
* **Interactive Web UI:** Provides a sleek local web interface to easily select your desired datasets (Actions, Classes, Items, Spells, etc.) and apply specific subset filters like spell level, magic item rarity, or attunement requirements.
* **Custom Visual Overrides:** Easily swap out card backgrounds, watermarks, and card backs. The UI automatically scans your `icons` folder for available SVGs to choose from, or you can upload your own custom `.svg` files directly through the web interface.
* **Printable Card Backs:** Generate perfectly sized, 3x3 grid pages of card backs with a single click, ready to be printed on the reverse side of your decks.
* **Dynamic Formatting:** Don't worry about long text walls. The engine intelligently calculates text length and table sizes, automatically splitting massive class features or complex spell descriptions across multiple consecutive cards.
* **Zero Dependencies Required:** You don't need Python or Git installed on your system. The installer automatically downloads a portable, isolated Python 3.14 environment specifically for this tool.
* **Always Up to Date:** The installer directly clones the latest 5etools data repository, and the launcher checks both the generator and data sets are up to date, ensuring you always have access to the newest releases and errata.

##  Installation

This tool is designed to run on **Windows** and requires an active internet connection for the initial setup. You can run **`card_controller.py`** directly if you'd rather go through it manually. That will require you to clone the 5eTools dataset repo manually in the generators root folder. 

1. Download **`install.bat`** (skip to step 3 if downloading just the installer) or the latest release from the [Releases](https://github.com/bankenichi/5.5e-Card-Generator-for-5eTools/releases) page, or download the repository directly.
2. Extract the folder to your desired location (e.g., your Documents folder).
3. Double-click **`install.bat`**. 
   * *Note: The installer will download a portable Python environment, pull the necessary generator files, and clone the massive 5etools dataset. This might take a few minutes depending on your internet connection.*

##  How to Use

1. Double-click **`launch.bat`**. This will start the local server and automatically open the Controller UI in your default web browser.
2. **Select Datasets:** Check the boxes for the datasets you want to include (e.g., Spells, Items, Optional Features).
3. **Apply Filters:** When you select a dataset, subset filters will appear. Use these to narrow down your deck (e.g., only generate Level 1-3 Evocation spells, or only Rare items that require attunement).
4. **Customize Visuals (Optional):** Use the Visual Options panel to select different backgrounds, watermarks, or card backs from your `icons` folder, or upload your own custom `.svg` files to override the defaults.
5. Click **Generate Deck** to create your cards.
6. Once complete, click the **Open Custom Deck** button. Your cards will open in a new tab as `Custom_Deck_Cards.html`.
7. **Generate Card Backs (Optional):** Need backs for your printed cards? Click **Generate Backs** to create a printable 3x3 grid of your selected card back design.

##  Printing Instructions
The output HTML is optimized for standard US Letter (8.5" x 11") printing.
* Press `Ctrl + P` in your browser.
* Set Paper Size to **Letter**.
* Set Margins to **None**.
* Make sure **Background graphics** are enabled so the card borders and icons print correctly.
* Save to PDF (might take a long time or timeout, depending on how many cards are being generated and printed at once) or print directly to cardstock!

##  Troubleshooting

**"ModuleNotFoundError" when launching:**
Make sure you ran `install.bat` completely. If you are updating from an older version, delete the `python-env` folder and run `install.bat` again to pull the correct environment.

**Cards are clipping or overflowing:**
The engine attempts to auto-scale fonts, but very dense tables might still push limits. Check the generated HTML to see how the engine chunked the data.

##  Tips, if you feel like it

**ko-fi.com/bankenichi**