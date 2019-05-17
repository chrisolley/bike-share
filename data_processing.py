import numpy as np
import pandas as pd
import datetime
import glob
from user_definition import *
import simplejson
import urllib
from polyline.codec import PolylineCodec


def read_data(read_all=True, fname=None):
    '''
    Read in data to pandas dataframe
    '''
    if fname is not None:
        return pd.read_csv(fname)
    if read_all:
        trip_data = []
        for fname in glob.glob('data/*.csv'):
            trip_data.append(pd.read_csv(fname))
        return pd.concat(trip_data, axis=0)


def get_path(polyline):
    '''
    Obtain path latitudes and longitudes from polyline.
    '''
    coords = PolylineCodec().decode(polyline)
    path_lats = [coord[0] for coord in coords]
    path_lons = [coord[1] for coord in coords]
    return path_lats, path_lons


def get_polyline(orig, dest):
    '''
    Obtain path polyline from origin, destination (lat, lon)
    tuple, using google maps directions api.
    '''
    orig_lat, orig_lon = orig[0], orig[1]
    dest_lat, dest_lon = dest[0], dest[1]
    url = 'https://maps.googleapis.com/maps/api/directions/json?origin=%s,%s&destination=%s,%s&mode=bicycling&key=%s' % (orig_lat, orig_lon, dest_lat, dest_lon, API_KEY)
    result = simplejson.load(urllib.request.urlopen(url))
    polyline = result['routes'][0]['overview_polyline']['points']
    return polyline


def floor_time_to_min(tm, min):
    '''
    Convenience function for flooring datetime to nearest min minutes
    '''
    return tm - datetime.timedelta(minutes=tm.minute % min,
                                   seconds=tm.second,
                                   microseconds=tm.microsecond)

if __name__ == "__main__":
    trip_df = read_data()
    # trip_df = read_data('data/201904-fordgobike-tripdata.csv')
    idx = (trip_df.start_station_longitude > -122.528114) & \
          (trip_df.start_station_longitude < -122.343407) & \
          (trip_df.start_station_latitude > 37.705825) & \
          (trip_df.start_station_latitude < 37.815209)
    trip_df = trip_df[idx]
    trip_df.to_csv('data/fordgobike-tripdata.csv')
