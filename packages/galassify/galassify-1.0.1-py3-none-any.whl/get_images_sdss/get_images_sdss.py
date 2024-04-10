"""
SDSS image downloader: Tool to download galaxy images from SDSS.
Written by Simon, adapted by Andoni
""" 

import argparse
from pathlib import Path

import pandas as pd
import numpy as np

import requests
from io import BytesIO
from PIL import Image

from galassify.utils import dir_file, dir_path

VERSION = "0.1"

# Define functions
def download_sdss(fname:str, raval:float, decval:float, size:int) -> None:
    """Cutout.
    Download sdss images using ra and dec using DR12 [it is the same for DR16].
    We have considered 0.1 ''/pix, it can be modify changing the scale value or the width/height in url_1 variable.
    The parameter "name" correspond with the SIG name.
    Initially, I have created a folder called as sdss_fig to download there all the figures from sdss.
    """
    r = requests.get(f'http://skyserver.sdss.org/dr12/SkyserverWS/ImgCutout/getjpeg?TaskName=Skyserver.Chart.Image&ra={raval}&dec={decval}&scale=0.35&width={size}&height={size}&opt=G&query=&Grid=on')
    Image.open(BytesIO(r.content)).save(fname)

def get_args():
    parser = argparse.ArgumentParser(prog='SDSS image downloader', description="")

    parser.add_argument('--version', action='version', version='%(prog)s ' + VERSION,
                        help="Prints software version and exit.\n")
    parser.add_argument('-p', '--path', type=dir_path, default='img',
                        help="Path to save image files.\n")
    parser.add_argument('-i', '--inputfile', type=dir_file, default='galaxies.csv',
                        help="Galaxy database file in *.csv format.\n")
    parser.add_argument('-o', '--outputfile', type=str, default=None,
                        help="""Output galaxy database file in *.csv format containing 
                        the path to the downloaded images. If not specified, the
                        paths will be written in the input CSV file.""")
    parser.add_argument('-s', '--size', type=int, default=512,
                        help="Size of the edges (in pixels) of the downloaded images.\n")
    
    return parser.parse_args()

def main():
    # Params
    args = get_args()
    path = Path(args.path)
    inputfile = Path(args.inputfile)
    size = args.size
    outputfile = args.outputfile
    # Read catalogue
    galaxies = pd.read_csv(inputfile)

    # Download images
    n = len(galaxies)
    print(f"Downloading images from SDSS for {n} galaxies")
    try:
        for index, row in galaxies.iterrows():
            id = row['galaxy']
            group = '-'
            if 'group' in galaxies.columns:
                group = row['group']
                
            fname = f"{path}/img_{group}_{id}.jpeg"
            download_sdss(fname, row['ra'], row['dec'], size)
            galaxies.loc[index, 'filename'] = f"img_{group}_{id}.jpeg"
            
            if index % 10 == 0:
                print(f"Remaining {n-index}")
    except KeyError as e:
        print(f"KeyError: {e}")
    
    file = Path(outputfile) if outputfile else inputfile
    galaxies.to_csv(file, index=None)
    print("Done!")

if __name__ == '__main__':
    sys.exit(main())
