import functools
import pandas as pd
import datetime as dt
import unicodedata
from dateutil import tz
from tzlocal import get_localzone

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from Servr.db import get_db
from Servr.auth import login_required

bp = Blueprint('showdata', __name__)
@bp.route('/', methods=('GET', 'POST'))
@login_required
def index():
    if request.method == 'POST':
        start = request.form['date-start']
        end = request.form['date-end']
        querystr = "SELECT * FROM envdata WHERE [datetime] >= date('{}') AND [datetime] <= date('{}','+1 day') ORDER BY [datetime] ASC ;" .format(start,end) # AND [datetime] <= date({})
       
        
    else:
        querystr = "SELECT * FROM envdata WHERE [datetime] >= date('now', '-1 days') ORDER BY [datetime] ASC ;"
        endobj = dt.datetime.now(get_localzone())
        end = endobj.strftime("%Y-%m-%d")
        startobj = endobj - dt.timedelta(1)
        start = startobj.strftime("%Y-%m-%d")
        
    db = get_db()
    currentparams = db.execute(
        'SELECT temperature, rh, co2 FROM params;').fetchall()
#    print(querystr)
    df = pd.read_sql_query(querystr, db)
    df.fillna(0, inplace=True)
   # df2 = pd.read_sql('select CONVERT(datetime, CHAR(10)) as datetime from envdata', db, parse_dates={'datetime': "%Y-%m-%d %H:%M:%S"})
    datetime = df['datetime'].str.normalize('NFKD').str.encode('ASCII').values.tolist() # x axis
    #datetime = ['2021-11-26 16:36:37', '2021-11-26 16:36:42',' 2021-11-26 16:36:47', '2021-11-26 16:36:52','2021-11-26 16:36:57']
#    print (type(datetime), datetime)
#    print (type(datetime[-1]), datetime[-1])
    
    rh = df['rh'].values.tolist()
    temperature = df['temperature'].values.tolist()
    o2 = df['o2'].values.tolist()
    co2 = df['co2'].values.tolist()
    airspeed = df['airspeed'].values.tolist()
    
    heater_list = df['temp_relay'].multiply(100).values.astype(int).tolist()
    humidifier_list = df['rh_relay'].multiply(100).values.astype(int).tolist()
    co2Solenoid_list = df['co2_relay'].multiply(100).values.astype(int).tolist()
    
    
    # current Data 
    relayquerystring = 'SELECT * FROM currentstates;'
    relaydf= pd.read_sql_query(relayquerystring, db)
    
    temp_current = relaydf['temperature'].values.tolist()
    rh_current = relaydf['rh'].values.tolist()
    co2_current = relaydf['co2'].values.tolist()
    o2_current = relaydf['o2'].values.tolist()
    airspeed_current = relaydf['airspeed'].values.tolist()
    heaters_current =  relaydf['temp_relay'].values.astype(int).tolist()
    humidifier_current = relaydf['rh_relay'].values.astype(int).tolist()
    co2Solenoid_current = relaydf['co2_relay'].values.astype(int).tolist()
    print(heaters_current,humidifier_current,co2Solenoid_current,temp_current, rh_current, co2_current, o2_current)
    
    return render_template('showdata/index.html',
                           start=start, end=end, datetime=datetime,
                           temperature = temperature, rh=rh,co2=co2,o2=o2,airspeed=airspeed,
                           
                           heater_list= heater_list, humidifier_list=humidifier_list,
                           co2Solenoid_list=co2Solenoid_list,
                           
                           currentparams=currentparams,
                           heaters_current=heaters_current, humidifier_current = humidifier_current,
                           co2Solenoid_current=co2Solenoid_current,
                           temp_current=temp_current, rh_current=rh_current, co2_current=co2_current,
                           o2_current=o2_current, airspeed_current=airspeed_current)