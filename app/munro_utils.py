import datetime
from time import sleep

import requests
import pandas as pd
import json
import numpy as np
import matplotlib.pyplot as plt
import os
from collections import deque
from app import app

OWM_API_KEY = "279d011609809fa0059ce17eb29dcba8"
EARTH_RADIUS = 6378.0
munro_pd = pd.read_csv("app/static/resources/munro_db.csv")
DATE_FORMAT = '%d/%m/%Y, %H:%M:%S'
MUNRO_PATH = os.path.join(os.path.dirname(app.root_path), "munros.txt")
LAST_REQUESTED_PATH = os.path.join(os.path.dirname(app.root_path), "last_written.txt")

class Mountain(object):
    """ class to represent a mountain and its weather forecast data"""

    def __init__(self, lat, long, name, last_requested=None, hilltype="munro"):
        self.hilltype = hilltype
        self.lat = lat
        self.long = long
        self.name = name
        self.hourly = None
        self.daily = None
        self.current = None
        self.add_owm_hourly()
        self.last_requested = last_requested

    @property
    def time_str(self):
        return self.last_requested.strftime("%d/%m/%Y, %H:%M:%S")

    def add_owm_hourly(self):
        " populate class with hour"
        forecast_json = requests.get(
            f"https://api.openweathermap.org/data/2.5/onecall?lat={self.lat}&lon={self.long}&exclude=minutely, alerts&appid={OWM_API_KEY}")

        forecast_dict = json.loads(forecast_json.text)

        hours_list = deque()
        for i, data in enumerate(forecast_dict['hourly']):

            try:
                rain = data['rain']['1h']
            except KeyError:
                rain = None
            try:
                snow = data['snow']['1h']
            except KeyError:
                snow = None

            entry = [data['dt'], data['temp'], data['feels_like'], data['wind_speed'], data['clouds'], data['pop'],
                     rain, snow]

            hours_list.append(entry)

        self.hourly = pd.DataFrame(hours_list,
                                   columns=["time", "temp", "feels_like", "wind_speed", "cloudiness",
                                            "precipitation %",
                                            "rain", "snow"])
        self.hourly = self.hourly.replace({np.nan: None})

        self.hourly["time"] = (self.hourly["time"] - self.hourly["time"].min())/3600
        self.hourly["temp"] = self.hourly["temp"] - 273.15   # convert to celsius
        self.hourly["feels_like"] = self.hourly["temp"] - 273.15  # convert to celsius

    def __dict__(self):

        d = {"lat": self.lat, "long": self.long, "name": self.name, "last_requested": self.time_str}
        d = {**d, **{c: list(self.hourly[c]) for c in self.hourly}}
        return d


def lat_long_bounds(search_lat, search_long, radius):

  # bounds for initial quick filter (a square up to min/max lats and longs)
    lat_upper = search_lat + np.rad2deg(radius/EARTH_RADIUS)
    lat_lower = search_lat - np.rad2deg(radius/EARTH_RADIUS)
    long_upper = search_long + np.rad2deg((np.arcsin(radius/EARTH_RADIUS) / np.cos(np.radians(search_lat))))
    long_lower = search_long - np.rad2deg((np.arcsin(radius/EARTH_RADIUS) / np.cos(np.radians(search_lat))))

    return lat_upper, lat_lower, long_upper, long_lower


def great_circle_arc_length(lat1, lat2, long1, long2):
    lat1, lat2, long1, long2 = map(lambda x: np.radians(x), [lat1, lat2, long1, long2])

    dist = np.arccos(np.sin(lat1)*np.sin(lat2) + np.cos(lat1)*np.cos(lat2)*np.cos(long1-long2)) * EARTH_RADIUS

    return dist


def filter_munros(munro_pd, search_lat, search_long, search_radius):
    lat_upper, lat_lower, long_upper, long_lower = lat_long_bounds(search_lat, search_long, search_radius)

    # filter munros to those that are in square
    munro_pd_1 = munro_pd[((munro_pd['lat'] >= lat_lower) & (munro_pd['lat'] <= lat_upper)) &
                          ((munro_pd['long'] >= long_lower) & (munro_pd['long'] <= long_upper))
                          & (munro_pd['category'] == "MUN")]

    # filter remaining munros to those that are in circle
    munro_pd_2 = munro_pd_1[
        great_circle_arc_length(munro_pd_1['lat'], search_lat, munro_pd_1['long'], search_long) <= search_radius]

    return munro_pd_2


def plot_munros(munro_list):
    fig, ax = plt.subplots(2, 2)
    titles = ['precipitation %', 'temp', 'wind_speed', 'cloudiness']
    for munro in munro_list:
        munro.add_owm_hourly()
        for a, title in zip(ax.flatten(), titles):
            a.scatter(munro.hourly['time'], munro.hourly[title], label=munro.name)

    for a, title in zip(ax.flatten(), titles):
        a.legend()
        a.grid(True)
        a.set_title(title)

    plt.show()


def write_munro_json():
    # initialise previous time as 5 hours before now
    if os.path.exists(LAST_REQUESTED_PATH):
        with open(LAST_REQUESTED_PATH, 'r') as munro_file:
            last_requested_json = json.load(munro_file)
            previous_time = datetime.datetime.strptime(last_requested_json["last_requested"], DATE_FORMAT)
    else:
        previous_time = datetime.datetime.now() - datetime.timedelta(hours=5)

    # run continuously until process running function is terminated
    while True:
        current_time = datetime.datetime.now()
        # refresh data every 4.5 hours
        if (current_time - previous_time) > datetime.timedelta(hours=4.5):
            filtered_munro_pd = munro_pd[(munro_pd['category'] == "MUN")]
            previous_time = datetime.datetime.now()
            prev_time_str = previous_time.strftime(DATE_FORMAT)
            print(f"requesting munro data at: {prev_time_str}")
            munro_list = [Mountain(munro.lat, munro.long, munro.Name, previous_time) for munro in filtered_munro_pd.itertuples()]
            munro_json = json.dumps([munro.__dict__() for munro in munro_list])
            with open(MUNRO_PATH, 'w') as outfile:
                outfile.writelines(munro_json)
            with open(LAST_REQUESTED_PATH, 'w') as outfile:
                json.dump({"last_requested": prev_time_str}, outfile)
        sleep(60*60)

if __name__ == "__main__":
    write_munro_json()
