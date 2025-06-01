import sys
import gc
import os
import json
#import h3pandas
import pandas as pd
import geopandas as gpd
from glob import glob
from datetime import datetime, timedelta

import warnings
warnings.filterwarnings('ignore')
warnings.simplefilter(action='ignore', category=FutureWarning)

INPUT_DATA_FOLDER = "../data/"

from r5py import TransportNetwork, TravelTimeMatrixComputer, TransportMode

def removeNetworkCache():
    filePaths = glob(INPUT_DATA_FOLDER+"network.osm.pbf.mapdb*")
    for filePath in filePaths: os.remove(filePath)
    return

def buildNetwork(YEAR):
    return TransportNetwork(INPUT_DATA_FOLDER+"network.osm.pbf", [INPUT_DATA_FOLDER+f"gtfs/{str(YEAR)}.zip"])
    #return TransportNetwork(INPUT_DATA_FOLDER+"network.osm.pbf")

def MatrixComputerObject(network, origins, destinations, departure, modes, max_time):
    return TravelTimeMatrixComputer(
        network,
        origins=origins,
        destinations=destinations,
        departure=departure,
        transport_modes=modes,
        max_time=timedelta(minutes=max_time),
        max_public_transport_rides=2,
        max_time_walking=timedelta(minutes=30),
        max_time_cycling=timedelta(minutes=45),
        departure_time_window=timedelta(minutes=40)
    )

def computeCommutings(network, origins, destinations, year):

    print("Garbage collector: collected", "%d objects." % gc.collect())

    DEFAULT_HOUR = 6
    DEFAULT_MINUTE = 30

    if str(year)=='2013': departure = datetime(2013,8,7,DEFAULT_HOUR,DEFAULT_MINUTE)
    if str(year)=='2022': departure = datetime(2022,8,10,DEFAULT_HOUR,DEFAULT_MINUTE)

    print('STARTING MATRIX')
    MAX_TIME = 60
    MODES = [TransportMode.TRANSIT, TransportMode.WALK, TransportMode.BICYCLE]
    Matrix = MatrixComputerObject(network, origins, destinations, departure, MODES, MAX_TIME).compute_travel_times()
    print('OK MATRIX')

    print()

    return Matrix