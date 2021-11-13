import urllib.request
import urllib.error
from colorama import Fore
from colorama import Style
from contextlib import suppress
import os

# System call
os.system("")

# Function to download image
def download_image (link,name,artist,scrylink):
	try:
		# Try to download from MTG Pics
		urllib.request.urlretrieve(link, "mtgpics/" + name + " (" + artist + ").jpg")
		print(f"{Fore.GREEN}SUCCESS MTGP: {Style.RESET_ALL}" + name)
	except:
		# Failed so download from scryfall art crop
		print(f"{Fore.RED}MTGP is missing " + name + ", checking Scryfall...")
		try: 
			urllib.request.urlretrieve(scrylink, "scryfall/"+name+" (" + artist + ").jpg")
			print(f"{Fore.GREEN}SUCCESS SCRY: {Style.RESET_ALL}" + name)
		except:
			file1.write(name+'\n')
			print(f"{Fore.RED}FAILED ALL: {Style.RESET_ALL}" + name)

# Open the failed to find txt
file1 = open('failed.txt','w+')

# Download images - paste from google sheets (see readme for details)
# download_image("https://mtgpics.com/pics/art/vow/140.jpg", "Alchemist's Gambit","Zoltan Boros","https://c1.scryfall.com/file/scryfall-cards/art_crop/front/a/8/a8fbf5d3-4677-4bf0-891f-57d6dcddaff7.jpg?1636014631")

# Close the txt file
file1.close()

print("\nAll available files downloaded.\nSee failed.txt for images that couldn't be located.\n")