import pandas as pd
import os
from astropy.io import fits
from pathlib import Path
import numpy as np
import sys
from tqdm import tqdm


if __name__ == "__main__":
    ell_limit = sys.argv[1]
    fwhm_limit = float(sys.argv[2])
    try:
        ell_limit = float(ell_limit)
    except:
        print(f"[WARNING] Could not resolve limit ellipticity limit of {ell_limit}")
        print("[WARNING] Using default of 0.2")
        ell_limit = 0.2
    print(f"[INFO] Selecting images with ellipticity <= {ell_limit}")
    print(f"[INFO] Selecting images with seeing <= {fwhm_limit} arcsec")
    k = 1.5
    files,fwhm,ell,nsrc = np.loadtxt("ell_src.cat",
                                dtype=str,
                                unpack=True,usecols=(0,1,2,3))
    ell = ell.astype(float)
    fwhm = fwhm.astype(float)
    nsrc = nsrc.astype(int)
    df = pd.DataFrame(data={"file" : files, "fwhm": fwhm,"ellipticity" : ell, "sources" : nsrc})
    ol = len(df)
    df = df[df["ellipticity"] <= ell_limit]
    df = df[df["fwhm"] <= fwhm_limit]
    print(f"[INFO] Throwing out {1-len(df)/ol}% of images.")# ({len(df)}/{ol}).")
    print(f"[INFO] Final Images")
    print(df)
    print(len(df))
    #med = np.median(df["sources"])
    #std = np.std(df["sources"])
    #df = df[df["sources"] >= med-k*std]
    #df = df[df["sources"] <= med+k*std]
    #print(len(df))
    #exit()
    print("copying files")
    #for file in tqdm(df["file"]):
    #    os.system(f"cp {file} selected/")
            

