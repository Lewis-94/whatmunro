import json
import datetime
from time import sleep

import pandas as pd
from flask import render_template, jsonify
import os
from app import app
from app.munro_utils import filter_munros, Mountain, munro_pd, MUNRO_PATH
from app.munro_utils import write_munro_json

@app.route('/')
@app.route('/index')
def index():

    return render_template('index.html', title='Home')

@app.route('/get_all_munros/', methods=["GET"])
def _get_all_munros(search_lat=None, search_long=None, search_radius=None):

    if search_lat:
        filtered_munro_pd = filter_munros(munro_pd, search_lat, search_long, search_radius)
    else:
        filtered_munro_pd = munro_pd

        with open(MUNRO_PATH, "r") as lines_json:
            munro_json = lines_json.readlines()[0]    # json data is all in one line (readlines() returns list)

    return munro_json
