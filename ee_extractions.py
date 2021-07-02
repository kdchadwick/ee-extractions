
import ee
import datetime
import pandas as pd
import geopandas as gp
import glob
import math
import numpy as np
import matplotlib.pyplot as plt
from IPython.display import Image

# Personal functions
from extraction_export import extraction_export
from get_data_df import get_data_df
from getFlow import getFlow
from getFlow import getBasin
from getGeometry import getGeometry

ee.Initialize()

### TO CHANGE BETWEEN EXTRACTING WATERSHED VIA GAGE ID AND POINTS, SET WATERSHED = TRUE OR FALSE
watershed = False
gage = 11134800 #set these as optional inputs?
point_csv = 'data/coordinates.csv'
outputfile = 'exports/points_dana.csv'

def main():
  assets = pd.read_csv('data/layers_short.csv')
  assets['scale'] = assets['scale'].astype('float')

  pts, bounding_box, names = getGeometry(watershed, gage, point_csv)
  extraction_export(assets, pts, bounding_box, names, outputfile, watershed, gage)


if __name__ == "__main__":
  main()
