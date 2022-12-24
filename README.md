# MTG Art Downloader
Mass download MTG card arts using MTGPics with Scryfall as a backup source, downloaded images are named according to their card name with the artist in parenthesis, set code in brackets. Arts from mtgpics are put in one folder, scryfall art crops in another folder. If any cards couldn't be found from either source a "failed.txt" is populated with names of the missing cards so you can manually look for them. For additional help using this app, join our discord server (click the discord button below), we have a #downloader channel and can help with any questions.

<p align="center">
  <a href="http://mprox.link/discord">
    <img alt="Discord" src="https://img.shields.io/discord/889831317066358815?label=Discord&style=plastic">
  </a>
  <img alt="Maintenance" src="https://img.shields.io/badge/Maintained%3F-yes-brightgreen?style=plastic">
  <img alt="Passing" src="https://img.shields.io/github/actions/workflow/status/MrTeferi/MTG-Art-Downloader/py-test.yml?style=plastic">
  <img alt="GitHub" src="https://img.shields.io/github/license/MrTeferi/MTG-Art-Downloader?color=1082C2&style=plastic">
  <a href="https://github.com/MrTeferi/MTG-Art-Downloader/releases">
    <img alt="GitHub all releases" src="https://img.shields.io/github/downloads/MrTeferi/MTG-Art-Downloader/total?style=plastic">
  </a>
  <img alt="Python" src="https://img.shields.io/badge/python-3.6%2B-yellow?style=plastic">
</p>

# Setup - Executable Release
- Download the latest release
- Make a copy of this google sheet document on your account:  [google Spreadsheet][3] (optional)

# Setup - Python Version
We now use `poetry` as package manager ([link][1]):
- Python 3.6+
- Download this repository `git clone https://github.com/MrTeferi/MTG-Art-Downloader`
- If you don't have Python Poetry, simply install it with `scoop install poetry` or read more at ([link][1])
- Install dependencies `poetry install`
- Make a copy of this google sheet document on your account: [google Spreadsheet][2](optional)
- execute it with
```
    poetry run python main.py
```

# How to use with a Decklist
- Paste a decklist into the cards.txt file in the working directory of MTG Art Downloader
- Runt he downloader

# How to use with scryfall commands?
- After running the app, you can enter commands like so:
`set:mh2, power>:3, type:creature`
- This example will download images for all MH2 creatures with power greater than or equal to 3. Separate arguments with a comma, separate the key and value of the argument with a colon. Refer to the scryfall API documentation for more use cases.

# How to use with Google Sheet Script
- Open up your copy of the "MTG Art Downloader Script" google sheet
- In the FX for box A2 you can customize arguments for what cards you want to pull using the first variable, for example choose a given set, a given rarity (or range of rarities). Don't change the second variable, those are the columns that are generated. You can read more about arguments for this scryfall script here: https://github.com/scryfall/google-sheets
- Once your comfortable with the scryfall arguments, press enter and watch it populate. Copy the right most column.
- Paste those rows into the cards.txt file in the working directory, hit save.
- Run the downloader

# Config.ini
- You can choose the download folder and cards.txt naming conventions.
- You can choose whether to download all available arts or only one art.
- You can choose whether to only download unique art or all art even when duplicats are present.
- You can choose whether to ignore fullarts (supported only when download all is enabled)
- You can choose whether to download scryfall arts as a fallback
- You can choose whether to download ONLY scryfall arts.
- You can choose whether to include extras in the search, this includes un-sets and special championship cards.
- You can increase or decrease threads added per second depending on the speed of your internet.
- You can choose the naming convention for saving the downloaded images.

# Contributing
If you wish to contribute to this project:
- Before doing a PR always make sure to run `pre-commit run` to ensure your code is standardized
- Only commit with commitizen, add your changed files with `git add .` then `cz commit` and follow the prompts

[1]: https://python-poetry.org/docs/basic-usage/
[2]: https://docs.google.com/spreadsheets/d/1Gss4pwJZL_WzjNVFx6uDAviu1gpJdfN1fQUHbwNJl2o
[3]: https://docs.google.com/spreadsheets/d/1QnVoQ1gvz1N4TKnkJJ44_FHomy0gNoxZlaPSkua4Rmk
