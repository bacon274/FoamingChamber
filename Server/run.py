from Servr import create_app
from multiprocessing import Process, Value
from Servr.db import get_db
import time
# import relay module

app = create_app()


        
def compare_values(actualdict, targetdict):
        relaydict = {}
        for i in actualdict:
            if actualdict[i] < targetdict[i]:
                relaydict[i] = True
            else:
                relaydict[i] = False  
        return relaydict
                    
            
def update_relay(relaydict):
    ### takes some dict and updates the relay
    print(relaydict)

def get_sensor_values():
    ## some code here for serial read
    sensors_dict = {'temperature': 23, 'co2' : 5, 'rh' : 40}
    return sensors_dict

def get_targets():
    with app.app_context():
        db = get_db()
        currentparams = db.execute('SELECT temperature, rh, co2 FROM params;').fetchall()
        return currentparams[0]
    
def repeat_loop():
    while True:
        actuals = get_sensor_values()
        targets = get_targets()
        relaydict = compare_values(actuals,targets)
        update_relay(relaydict)
        ## CODE HERE TO UPDATE ACTUALS TABLE
        ## CODE HERE TO UPDATE RELAYS TABLE
        time.sleep(10)
    
p = Process(target= repeat_loop)
p.start()