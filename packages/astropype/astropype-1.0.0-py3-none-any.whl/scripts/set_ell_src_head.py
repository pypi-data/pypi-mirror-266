import numpy as np
import sys
import os

# accepts only one argument, which is the filtered sextractor catalogue for ellipticity

if __name__ == "__main__":
    try:
        file = sys.argv[1]
        fwhmv,ellv = np.loadtxt(file,usecols=(0,1),unpack=True)
        file = file.replace("_fil.cat",".fits")
        if len(ellv) == 0:
            ell = 1
            nsrc = 0
            fwhm = 0
        else:
            fwhm = np.nanmedian(fwhmv) * 3600
            ell = np.nanmedian(ellv)
            nsrc = len(ellv)
        os.system(f"sethead ELL={ell} {file}")
        os.system(f"sethead NSOURCES={nsrc} {file}")
        os.system(f"sethead SEEING={fwhm} {file}")
    except:
        pass





