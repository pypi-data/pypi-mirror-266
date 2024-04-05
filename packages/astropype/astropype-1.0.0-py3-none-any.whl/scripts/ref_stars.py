import numpy as np





if __name__ == "__main__":
import pandas as pd
import os
from astropy.io import fits
from pathlib import Path
import numpy as np
import sys
from tqdm import tqdm


if __name__ == "__main__":
    ell_limit = sys.argv[1]
    try:
        ell_limit = float(ell_limit)
    except:
        print(f"[WARNING] Could not resolve limit ellipticity limit of {ell_limit}")
        print("[WARNING] Using default of 0.2")
        ell_limit = 0.2
    print(f"[INFO] Selecting images with ellipticity <= {ell_limit}")
    k = 1.5
    files,ell,nsrc = np.loadtxt("ell_src.cat",
                                dtype=str,
                                unpack=True,usecols=(0,1,2))
                
