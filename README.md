# MTG Art Downloader
This tool is intended to mass download arts for MTG Cards using MTGPics with Scryfall as a backup source, images are automaticalled named according to their card name with the artist in parenthesis. Arts from mtgpics are put in one folder, scryfall art crops in another folder. If any cards couldn't be found from either source a "failed.txt" is populated with names of the missing cards so you can manually look for them.

# Requirements
- Python 3
- pip install -r requirements.txt (python dependencies)
- Make a copy of this google sheet document on your account: https://docs.google.com/spreadsheets/d/1Gss4pwJZL_WzjNVFx6uDAviu1gpJdfN1fQUHbwNJl2o/edit?usp=sharing (optional)

# How to use with a Decklist
- Paste a decklist into the cards.txt file in the working directory of MTG Art Downloader
- Execute Run.bat, choose option 2. That's pretty much it.

# How to use with Google Sheet Script
- Open up your copy of the "Generate MTG Download Script V2" google sheet
- In the FX for box A2 you can customize arguments for what cards you want to pull using the first variable, for example choose a given set, a given rarity (or range of rarities). Don't change the second variable, those are the columns that are generated. You can read more about arguments for this scryfall script here: https://github.com/scryfall/google-sheets
- Once your comfortable with the scryfall arguments, press enter and watch it populate. Copy all of the filled in rows under the "Python script" column
- Paste those rows into the "sheet_generated.py", line 9 under the "PASTE GOOGLE SHEET CODE HERE" comment. Hit save.
- Execute "Run.bat", choose option 1. That's pretty much it.

# Settings.py
- You'll find all settings for this app in settings.py
- You can rename and change how folders are organized at the top
- You can choose whether to ignore fullarts (supported for mass downloading via decklist only)
- You can choose whether to download all arts or only one art for mass downloading via decklist
