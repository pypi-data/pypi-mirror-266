from spiakid_DRS.SpectralRes import Detect as D
import os
import argparse
from pathlib import Path
import pathlib

"""
Link between Terminal and pipeline
"""
def parse():
    # read in command line arguments
    parser = argparse.ArgumentParser(description='MKID Pipeline CLI')
    parser.add_argument('--init', action='store_true', help='launch the interface')
    parser.add_argument('--outp', help='output destination', dest='out_cfg', default=None)
    parser.add_argument('--inp', help='data location', dest='in_cfg' , default=None)
    parser.add_argument('--format', help='format of the plot', default='.jpg', dest='form')
    parser.add_argument('--dir', help='create input and output folder', action='store_true')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse()

    if args.init:
        try:
            path = str(sorted(pathlib.Path('/').glob('**/Home.py'))[0]) #Docker version
        except:
            path = str(sorted(pathlib.Path('').glob('**/Home.py'))[0])  #Terminal version

        os.system("streamlit run "+path)
    
  