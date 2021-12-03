import urllib.request
import urllib.error
from colorama import Fore
from colorama import Style
from contextlib import suppress
from pathlib import Path
import os

# Define your setcode here
mtg_set = "vow";

# System call
os.system("")

# Create folders if they don't exist
Path(mtg_set).mkdir(mode=511, parents=True, exist_ok=True)
Path(mtg_set + "/mtgpics").mkdir(mode=511, parents=True, exist_ok=True)
Path(mtg_set + "/scryfall").mkdir(mode=511, parents=True, exist_ok=True)

# Function to download image
def download_image (set,code,name,artist,scrylink,flipname):
	link = "https://mtgpics.com/pics/art/"+set+"/"+code+".jpg";
	fliplink = "https://mtgpics.com/pics/art/"+set+"/"+code+"-2.jpg"
	flipscry = scrylink.replace("front","back")
	try:
		# Try to download from MTG Pics
		urllib.request.urlretrieve(link, mtg_set+"/mtgpics/" + name + " (" + artist + ").jpg")
		print(f"{Fore.GREEN}SUCCESS MTGP: {Style.RESET_ALL}" + name)
	except:
		# Failed so download from scryfall art crop
		print(f"{Fore.RED}MTGP is missing " + name + ", checking Scryfall...")
		try: 
			urllib.request.urlretrieve(scrylink, mtg_set+"/scryfall/"+name+" (" + artist + ").jpg")
			print(f"{Fore.GREEN}SUCCESS SCRY: {Style.RESET_ALL}" + name)
		except:
			file1.write(name+'\n')
			print(f"{Fore.RED}FAILED ALL: {Style.RESET_ALL}" + name)
	# Do flip card images
	if flipname != "":
		print(f"{Fore.GREEN}FLIP card found: {Style.RESET_ALL}" + flipname)
		try:
			# Try to download flip from MTG Pics
			urllib.request.urlretrieve(fliplink, mtg_set+"/mtgpics/" + flipname + " (" + artist + ").jpg")
			print(f"{Fore.GREEN}SUCCESS MTGP: {Style.RESET_ALL}" + flipname)
		except:
			# Failed so download from scryfall art crop
			print(f"{Fore.RED}MTGP is missing " + flipname + ", checking Scryfall...")
			try: 
				urllib.request.urlretrieve(scrylink, mtg_set+"/scryfall/"+flipname+" (" + artist + ").jpg")
				print(f"{Fore.GREEN}SUCCESS SCRY: {Style.RESET_ALL}" + flipname)
			except:
				file1.write(flipname+'\n')
				print(f"{Fore.RED}FAILED ALL: {Style.RESET_ALL}" + flipname)

# Open the failed to find txt
file1 = open(""+mtg_set+"/failed.txt","w+")

# Download images - paste from google sheets (see readme for details)
download_image("vow", "139", "Abrade","Dominik Mayer","https://c1.scryfall.com/file/scryfall-cards/art_crop/front/a/0/a0e47d11-cb21-402b-a39e-588a94cc57b4.jpg?1635791665", "")
download_image("vow", "1", "Adamant Will","Irina Nordsol","https://c1.scryfall.com/file/scryfall-cards/art_crop/front/b/d/bd091f3e-5fcc-4d12-b0c3-3b6340ab01d8.jpg?1636110000", "")
download_image("vow", "92", "Aim for the Head","Zoltan Boros","https://c1.scryfall.com/file/scryfall-cards/art_crop/front/1/1/1174e8e1-2e8e-4070-9871-7d5d93e0dd56.jpg?1636119052", "")
download_image("vow", "140", "Alchemist's Gambit","Zoltan Boros","https://c1.scryfall.com/file/scryfall-cards/art_crop/front/a/8/a8fbf5d3-4677-4bf0-891f-57d6dcddaff7.jpg?1636014631", "")
download_image("vow", "47", "Alchemist's Retrieval","David Auden Nash","https://c1.scryfall.com/file/scryfall-cards/art_crop/front/e/d/edbf9d4f-6027-40b8-81c1-7f001a9119dd.jpg?1636113921", "")
download_image("vow", "141", "Alluring Suitor","Justine Cruz","https://c1.scryfall.com/file/scryfall-cards/art_crop/front/3/9/397ffd01-c090-4233-9f5a-5f765886d498.jpg?1636584765", "Deadly Dancer")
download_image("vow", "142", "Ancestral Anger","Randy Vargas","https://c1.scryfall.com/file/scryfall-cards/art_crop/front/5/d/5dee47ab-d603-4346-97f4-a25dc3f47765.jpg?1636115944", "")
download_image("vow", "230", "Ancient Lumberknot","Nicholas Gregory","https://c1.scryfall.com/file/scryfall-cards/art_crop/front/2/2/22264087-bac4-4746-b6ce-0d44cce163e6.jpg?1636208854", "")
download_image("vow", "2", "Angelic Quartermaster","PINDURSKI","https://c1.scryfall.com/file/scryfall-cards/art_crop/front/4/1/41d81b88-c19b-4148-89ba-ae8fb53843e1.jpg?1635927548", "")
download_image("vow", "231", "Anje, Maid of Dishonor","Yongjae Choi","https://c1.scryfall.com/file/scryfall-cards/art_crop/front/1/b/1bfac4ab-97f1-448c-8554-42ed03eb5656.jpg?1636208871", "")
download_image("vow", "185", "Apprentice Sharpshooter","Steve Prescott","https://c1.scryfall.com/file/scryfall-cards/art_crop/front/f/0/f03f0790-cdc9-4bb4-ae54-2c248435b0a4.jpg?1635454549", "")
download_image("vow", "93", "Archghoul of Thraben","Johann Bodin","https://c1.scryfall.com/file/scryfall-cards/art_crop/front/0/c/0cf81c9d-ddb2-470e-8a4a-590049713e95.jpg?1635532299", "")
download_image("vow", "3", "Arm the Cathars","Zoltan Boros","https://c1.scryfall.com/file/scryfall-cards/art_crop/front/2/0/2004a20c-e434-4691-8ef2-740846ce6a51.jpg?1636208251", "")
download_image("vow", "186", "Ascendant Packleader","Alessandra Pisano","https://c1.scryfall.com/file/scryfall-cards/art_crop/front/1/4/142c5b67-5de9-41da-b57f-7ce771457a3e.jpg?1635793324", "")
download_image("vow", "187", "Avabruck Caretaker","Heonhwa Choe","https://c1.scryfall.com/file/scryfall-cards/art_crop/front/c/0/c0c358b4-5af2-438f-8bd5-beb0ee6b518b.jpg?1636755272", "Hollowhenge Huntmaster")
download_image("vow", "143", "Ballista Watcher","Tomas Duchek","https://c1.scryfall.com/file/scryfall-cards/art_crop/front/6/3/63d96c52-66ce-4b46-9a0b-7cd9a43f9253.jpg?1636755315", "Ballista Wielder")
download_image("vow", "144", "Belligerent Guest","Darren Tan","https://c1.scryfall.com/file/scryfall-cards/art_crop/front/1/b/1bb844c4-f41c-4411-a80a-c19e1d97b272.jpg?1635890561", "")
download_image("vow", "48", "Binding Geist","Campbell White","https://c1.scryfall.com/file/scryfall-cards/art_crop/front/7/3/730e4629-dc54-415d-9493-88885788ca19.jpg?1636494265", "Spectral Binding")
download_image("vow", "49", "Biolume Egg","Filip Burburan","https://c1.scryfall.com/file/scryfall-cards/art_crop/front/5/7/57039230-bf5a-4489-9dc1-37e27b17bd84.jpg?1637519689", "Biolume Serpent")

# Close the txt file
file1.close()

print("\nAll available files downloaded.\nSee failed.txt for images that couldn't be located.\n")