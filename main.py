import sys
from PIL.ExifTags import TAGS
from PIL import Image
import subprocess
import re


def main() :
    args = sys.argv[1:]

    if len(args) != 2 or args[0] not in  ["-map" , "-steg"]:
        print("Invalid args")
        return

    try:
        image = Image.open(args[1])
        exifdata = image.getexif()
    except :
        print("Invalid Image")
        return

    match args[0] :
        case "-map" :
            getLoc(exifdata)
        case _ :
            getSteg(args[1])


def getSteg(file_path) :

    try :
        filecontent = extract_strings(file_path) 
        start_block = "-----BEGIN PGP PUBLIC KEY BLOCK-----"
        end_block = "-----END PGP PUBLIC KEY BLOCK-----"

        start = filecontent.index(start_block)
        end  = filecontent.rindex(end_block)
        print(filecontent[start:end+len(end_block)])
       
    except :
        print("No steg")


def extract_strings(file_path):
    try:
        result = subprocess.run(['strings', file_path], capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'exécution de strings : {e}")

def getLoc(exifdata) :
    info_dict = {}

    for tag_id in exifdata :
        tag = TAGS.get(tag_id, tag_id)

        if tag == "GPSInfo" :
            data = exifdata.get_ifd(tag=tag_id)
            
            latitude_data = dms_to_decimal(data.get(2) ,data.get(1) )
            longitude_data = dms_to_decimal(data.get(4) ,data.get(3) )
            if not (latitude_data == None or longitude_data == None):
                tag = "Lat/Lon"
                data = f"({latitude_data:3f}) / ({longitude_data:3f})"
        
            info_dict[tag] = data

    if(info_dict.get("Lat/Lon")) :
        info_str = "\n".join([f"{n:25}: {info}" for n, info in info_dict.items()])
        print(info_str)
    else :
        print("No loc info")


def dms_to_decimal(gpsinfo , direction):

    if  gpsinfo == None or direction == None :
        return None

    degrees = gpsinfo[0]
    minutes = gpsinfo[1]
    seconds = gpsinfo[2]
    
    decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)

    if direction in ['S', 'W']:
        decimal = -decimal
    
    return decimal


main()