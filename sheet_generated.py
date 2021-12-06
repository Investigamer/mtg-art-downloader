# Import download image function
import settings
from downloader import download_image

# Open the failed to find txt
failed = open(settings.f_name+"/failed.txt","w+")

# PASTE GOOGLE SHEET CODE HERE
download_image(failed,"vow", "139", "Abrade","Dominik Mayer","https://c1.scryfall.com/file/scryfall-cards/art_crop/front/a/0/a0e47d11-cb21-402b-a39e-588a94cc57b4.jpg?1635791665", "")
download_image(failed,"vow", "1", "Adamant Will","Irina Nordsol","https://c1.scryfall.com/file/scryfall-cards/art_crop/front/b/d/bd091f3e-5fcc-4d12-b0c3-3b6340ab01d8.jpg?1636110000", "")
download_image(failed,"vow", "92", "Aim for the Head","Zoltan Boros","https://c1.scryfall.com/file/scryfall-cards/art_crop/front/1/1/1174e8e1-2e8e-4070-9871-7d5d93e0dd56.jpg?1636119052", "")
download_image(failed,"vow", "140", "Alchemist's Gambit","Zoltan Boros","https://c1.scryfall.com/file/scryfall-cards/art_crop/front/a/8/a8fbf5d3-4677-4bf0-891f-57d6dcddaff7.jpg?1636014631", "")
download_image(failed,"vow", "47", "Alchemist's Retrieval","David Auden Nash","https://c1.scryfall.com/file/scryfall-cards/art_crop/front/e/d/edbf9d4f-6027-40b8-81c1-7f001a9119dd.jpg?1636113921", "")
download_image(failed,"vow", "141", "Alluring Suitor","Justine Cruz","https://c1.scryfall.com/file/scryfall-cards/art_crop/front/3/9/397ffd01-c090-4233-9f5a-5f765886d498.jpg?1636584765", "Deadly Dancer")

# Close the txt file
failed.close()

print("\nAll available files downloaded.\nSee failed.txt for images that couldn't be located.\n")