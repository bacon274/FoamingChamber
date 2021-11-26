import functools
import pandas as pd
from datetime import datetime

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from Servr.db import get_db
from Servr.auth import login_required

bp = Blueprint('showdata', __name__)
@bp.route('/')
@login_required
def index():
    db = get_db()
    currentparams = db.execute(
        'SELECT temperature, rh, co2 FROM params;').fetchall()
    #print(currentparams)
#    historicalData = db.execute(
#        'SELECT * FROM envdata;').fetchall()
#    rh = historicalData = db.execute(
#        'SELECT rh FROM envdata;').fetchall()
    df = pd.read_sql_query('SELECT * FROM envdata;', db) # parse_dates={'datetime':"%Y-%m-%d %H:%M:%S"}
#    df2 = pd.read_sql('select CONVERT(datetime, CHAR(10)) as datetime from envdata', db, parse_dates={'datetime': "%Y-%m-%d %H:%M:%S"})
    datetime = df['datetime'].values.tolist() # x axis

    rh = df['rh'].values.tolist()
    temperature = df['temperature'].values.tolist()
    o2 = df['o2'].values.tolist()
    co2 = df['co2'].values.tolist()
    airspeed = df['airspeed'].values.tolist()
    
    print (datetime)
    return render_template('showdata/index.html', datetime=datetime, temperature = temperature, rh=rh,co2=co2,o2=o2,airspeed=airspeed,currentparams=currentparams)