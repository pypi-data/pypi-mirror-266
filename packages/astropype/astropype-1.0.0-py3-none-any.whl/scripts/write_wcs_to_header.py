#writes .head files to an existing python header
from astropy.io import fits
import sys

def is_float(string : str):
    for char in [".","-","+","E"]:
        string = string.replace(char, "")
    if string.isnumeric():
        return True
    return False

def main():
    if len(args:=sys.argv) == 1:
        print("parse a file or multiple files")
        print("\t...exiting")
        exit()

    for file in args[1:]:
        headfile = file.replace(".fits",".head")
        print(f"writing header from {headfile} to {file}")
        try:
            with open(headfile) as hf:
                lines = hf.readlines()
        except:
            print("'.head' file not found.")
            print(f"\t...skipping {file}")
            continue
        for i,line in enumerate(lines):
            if i <= 2:
                continue
            keyword = line.split(" ")[0].replace("=","")
            if keyword == "END":
                break

            id = line.find("/")
            comment = line[id+2:].replace("\n","").lstrip(" ").rstrip(" ")
            value = line.split("=")[1].split("/")[0].replace(" ","").replace("'","")
            
            if is_float(value):
                value = float(value)
            else:
                value = str(value)
            fits.setval(file,keyword=keyword,value=value,comment=comment)

if __name__ == "__main__":
    main()
    
