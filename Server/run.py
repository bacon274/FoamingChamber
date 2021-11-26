from Servr import create_app
from multiprocessing import Process, Value
from Servr.db import get_db
import time
from datetime import datetime
from dateutil import tz
from tzlocal import get_localzone
# import relay module

app = create_app()


        
def compare_values(actualdict, targetdict):
        relaydict = {}
        for i in actualdict:
            if actualdict[i] < targetdict[i]:
                relaydict[i] = True
            else:
                relaydict[i] = False
        relaydict['uv'] = True    
        return relaydict
                    
            
def update_relay(relaydict):
    ### takes some dict and updates the relay
    print("Updating Relay: ", relaydict)

def get_sensor_values():
    ## some code here for serial read
    sensors_dict = {'actionable':{'temperature': 23, 'co2' : 5, 'rh' : 40}, 'other':{ 'airspeed': 5,'o2':18}}
    return sensors_dict

def get_targets():
    try:
        with app.app_context():
            db = get_db()
            currentparams = db.execute('SELECT temperature, rh, co2 FROM params;').fetchall()
            return currentparams[0]
    except:
        print("Error, no targets set")
            
            
    
def repeat_loop():
    while True:
        try:
            actuals = get_sensor_values()
            targets = get_targets()
            relaydict = compare_values(actuals['actionable'],targets)
            update_relay(relaydict)
            ## CODE HERE TO UPDATE ACTUALS TABLE
            ## CODE HERE TO UPDATE RELAYS TABLE
            time.sleep(10)
        except:
            print("couldnt run relay control")
            relaydict = {'temperature': False, 'co2' : False, 'rh' : False, 'uv': False}
            update_relay(relaydict)
            
def save_loop():
    while True:
        try:
            with app.app_context():
                now = datetime.now(get_localzone())
#                timestr = now.strftime("%H:%M:%S")
#                datestr = now.strftime("%Y-%m-%d")
                datetimestr = now.strftime("%Y-%m-%d %H:%M:%S")
                db = get_db()
                actuals = get_sensor_values()
                rh = actuals['actionable']['rh']
                co2 = actuals['actionable']['co2']
                o2 = actuals['other']['o2']
                airspeed = actuals['other']['airspeed']
                temperature = actuals['actionable']['temperature']
                print("Saving Data: ", datetimestr,temperature, rh, co2,o2,airspeed)
                db.execute(
                    'INSERT INTO envdata (datetime, temperature, rh, co2, o2, airspeed) VALUES (?,?,?,?,?,?)', (datetimestr, temperature, rh, co2, o2,airspeed ))
                db.commit()
        except:
            print('Error Saving')
        time.sleep(5)
        
def get_histdata():
        try:
            with app.app_context():
                db = get_db()
                historicaldata = db.execute('SELECT * FROM envdata;').fetchall()
                print('Historical data:', historicaldata)
        except:
            print('Cannot access DB')
        

def wipe_histdata():
    try:
        with app.app_context():
            db = get_db()
            db.execute("DELETE FROM envdata;")
            db.commit()
            print("Wiped historical data")
    except:
        print('Cannot wipe DB')
        
if __name__ == 'run':
#    wipe_histdata()
#    save_histdata()
    
    get_histdata()
#    p = Process(target= repeat_loop)
#    p.daemon = True
#    p.start()
#    savedataprocess = Process(target=save_loop)
#    savedataprocess.daemon = True
#    savedataprocess.start()
    
