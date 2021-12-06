# Import download image function
import settings
from downloader import download_image

# Open the failed to find txt
failed = open(settings.f_name+"/failed.txt","w+")

# PASTE GOOGLE SHEET CODE HERE


# Close the txt file
failed.close()

print("\nAll available files downloaded.\nSee failed.txt for images that couldn't be located.\n")