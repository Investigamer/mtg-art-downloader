# MTG Art Downloader
This tool is intended to mass download arts for MTG Cards using MTGPics with Scryfall as a backup source, images are automaticalled named according to their card name with the artist in parenthesis. Arts from mtgpics are put in one folder, scryfall art crops in another folder. If any cards couldn't be found from either source a "failed.txt" is populated with names of the missing cards so you can manually look for them.

# Requirements
- Python 3
- pip install -r requirements.txt (python dependencies)
- Make a copy of this google sheet document on your account: https://docs.google.com/spreadsheets/d/1zI4wF6EN2MO7DcZbqxqEcm8Fg1u-yMu_ycXFyPbqf0M/edit?usp=sharing

# How to use it
- Open up your copy of the "Generate MTG Download Script" google sheet
- In the FX for box A2 you can customize arguments for what cards you want to pull using the first variable, for example choose a given set, a given rarity (or range of rarities). Don't change the second variable, those are the columns that are generated. You can read more about arguments for this scryfall script here: https://github.com/scryfall/google-sheets
- Once your comfortable with the scryfall arguments, press enter and watch it populate. Copy all of the filled in rows under the "Python script" column
- Paste those rows into the "find.py", line 31 under the "Download Images" comment
- At the top of the "find.py" script change mtg_set to the set code you are using, if you so choose. The output folders will be generated in this named directory.
- Open powershell within the working directory
- Run: python find.py
- The script will begin downloading images instant, attempting to find MTG Pics art first (and sort them into the mtgpics folder). Any card arts that couldn't be found on mtgpics will instead be downloaded from scryfall (and sorted in the scryfall folder).
