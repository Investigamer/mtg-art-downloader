## v1.3.0 (2023-07-19)

### Fix

- **constants**: Change from Enum to dataclass
- **types**: Fixed return type of naming_convention
- **get_mtgp_page**: Covered more response cases in which card could not be located
- **sets**: Updated some set codes and promo code dictionary

### Feat

- **settings**: Added a setting to allow downloading full Scryfall scans instead of art crop

## v1.2.0 (2023-03-31)

### Feat

- **Downloader**: Move from threads to multiprocessing, complete rewrite with rate limited requests

## v1.1.9 (2022-08-28)

### Fix

- **scryfall**: Fixed scryfall downloading

## v1.1.8 (2022-08-07)

### Fix
- **codes**: Wrote a new comprehensive set replacement library
- **py-test.yml**: Add types-requests to workflow
- **mypy**: Added stronger typing, fixed mypy errors
- **Card-Settings**: Scryfall commands now pass direct scryfall data, improvements to download process
- **core.get_mtgp_code-console**: Added flush to console and fixed pop, get_mtgp_code can now fall back on named search

## 1.1.7 (2022-08-05)

### Fix
- **constants.py**: Add Thread lock to console, fix doubled up print lines
- **main.py**: Fix type error list not subscriptable
- **py-test.yml**: add types-requests to mypy workflow
- **py-test.yml**: fix mypy stub error "requests"
- **py-test.py-core.py-main.py**: Fix poetry usage and pathing
- **py-test.yml-main.py**: Fix type error, fix poetry usage

### Refactor
- **card.py**: Stronger typing, improved download methods, removed bare exceptions
- **core.py-pyproject.toml**: Added stronger typing

## Pre-1.1.7

- **Pre-Commitizen** - See GitHub release history
