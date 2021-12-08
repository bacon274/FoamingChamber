from Servr import create_app
from multiprocessing import Process, Value
from Servr.db import get_db
import pandas as pd
import time
from datetime import datetime
from dateutil import tz
from tzlocal import get_localzone
import serial
import json
import RPi.GPIO as GPIO
import threading
# import relay module

app = create_app()

# Set up RELAY
def relay_setup():
    # NOTE, GPIO.HIGH is off
#    global Relay_Ch1
#    global Relay_Ch2
#    global Relay_Ch3
#    global Relay_Ch4
#    global Relay_Ch5
#    global Relay_Ch6
#    global Relay_Ch7
#    global Relay_Ch8
    
    global relay_dict
    
    Relay_Ch1 = 5
    Relay_Ch2 = 6
    Relay_Ch3 = 13
    Relay_Ch4 = 16
    Relay_Ch5 = 19
    Relay_Ch6 = 20
    Relay_Ch7 = 21
    Relay_Ch8 = 26
    
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(Relay_Ch1,GPIO.OUT)
    GPIO.setup(Relay_Ch2,GPIO.OUT)
    GPIO.setup(Relay_Ch3,GPIO.OUT)
    GPIO.setup(Relay_Ch4,GPIO.OUT)
    
#    GPIO.output(Relay_Ch2,GPIO.HIGH)
#    GPIO.output(Relay_Ch3,GPIO.HIGH)
#    GPIO.output(Relay_Ch4,GPIO.HIGH)
#    GPIO.output(Relay_Ch1,GPIO.HIGH)
    
    relay_dict = {'temperature': {'ch': Relay_Ch1,'state':  False}, 'co2' : {'ch': Relay_Ch2,'state':  False}, 'rh' :  {'ch': Relay_Ch3,'state':  False}, 'uv':  {'ch': Relay_Ch4,'state':  False}}
#    update_relay()
    print("Setup The Relay Module is [success]")
  
def update_relay():
    for i in relay_dict:
        if relay_dict[i]['state'] == True:
            try:
                GPIO.output(relay_dict[i]['ch'],GPIO.LOW)
            except:
                print("except")
                GPIO.cleanup()
        elif relay_dict[i]['state'] == False:
            try:
                GPIO.output(relay_dict[i]['ch'],GPIO.HIGH)
            except:
                print("except")
                GPIO.cleanup()
    
    print("Updating Relay: ", relay_dict)
    
def compare_values(actualdict, targetdict):
#        print("check:",actualdict, targetdict)
        for i in targetdict:
            if actualdict[i] < targetdict[i]:
                relay_dict[i]['state'] = True
            else:
                relay_dict[i]['state'] = False
        relay_dict['uv']['state'] = True  

def get_sensor_values(ser):
#    print("getting sensor vals")
#    
#    try:
#        print("attempting to get ser")
#        ser = serial.Serial('/dev/ttyACM1', 9600, write_timeout=1, timeout=1)
#        
#    except serial.SerialException:
#        try:
#            print("attempting to get ser 2")
#            ser = serial.Serial('/dev/ttyACM0', 9600 ,write_timeout=1, timeout=1)
#        except Exception as e:
#            print(e)
#    print("ser established")   
    ser.reset_input_buffer()
#    print("reset ser buffer")
    
    try:
#        print("try started")
        ser.write(b"GO\n")
#        print("serial write")
        #ser.write("GO")
        time.sleep(1)
        
        line = ser.readline().decode('utf-8').rstrip()
#        print(line)
#        print("serial read")
        if line == "GO" :
            data = ser.readline().decode('utf-8').rstrip()
            sensors_dict = json.loads(data)
        else:
            sensors_dict = {}
#        print("try complete")    
            
    except Exception as e:
        print("EROOR: data stream")
        print(e)
        sensors_dict = {}
       # sensors_dict = {'actionable':{'temperature': 0, 'co2' : 0, 'rh' : 0}, 'other':{ 'airspeed': 0,'o2':0}}
    
#    ser.close()
    print("made it through sensor get")
    return sensors_dict

def get_targets():
    try:
        with app.app_context():
            db = get_db()
            querystr = 'SELECT temperature, rh, co2 FROM params LIMIT 1;'
            currentparams = db.execute('SELECT temperature, rh, co2 FROM params;').fetchall()
            #df = pd.read_sql_query(querystr, db)
            
           # rh = df['rh'].values.tolist()
            #temperature = df['temperature'].values.tolist()
           # co2 = df['co2'].values.tolist()
            #print(type(currentparams[0]), currentparams, currentparams[0][0]  )
            rh = currentparams[0][1]
            temperature = currentparams[0][0]
            co2 = currentparams[0][2]
            #print(rh, temperature, co2)
            current_params_dict = {'temperature': temperature, 'rh': rh, 'co2': co2}
            return current_params_dict
    except:
        print("Error, no targets set")
            
            
    
def repeat_loop(ser):
    print("starting relay loop")
    while True:
        
        try:
            #actuals = get_sensor_values()
            actuals = get_sensor_values(ser) #{'other': {'o2': 19.91613, 'airspeed': 0.588744}, 'actionable': {'temperature': 24.3, 'co2': 0, 'rh': 57}}
            #print("sensor vals:", actuals)
            targets = get_targets()
            #print("TARGETS", targets, "ACTUALS",actuals)
            compare_values(actuals['actionable'],targets)
            update_relay()
            ## CODE HERE TO UPDATE ACTUALS TABLE
            ## CODE HERE TO UPDATE RELAYS TABLE
            #print("made it through relay loop")
            time.sleep(10)
        except:
            print("couldnt run relay control")
#            relay_dict['temperature']['state'] = False
#            relay_dict['rh']['state'] = False
#            relay_dict['uv']['state'] = False
#            relay_dict['co2']['state'] = False
#            #relaydict = {'temperature': False, 'co2' : False, 'rh' : False, 'uv': False}
#            update_relay()
            time.sleep(7)
            

def save_loop(ser):
    print("starting save loop")
    while True:
        try:
            with app.app_context():
                now = datetime.now(get_localzone())
#                timestr = now.strftime("%H:%M:%S")
#                datestr = now.strftime("%Y-%m-%d")
                datetimestr = now.strftime("%Y-%m-%d %H:%M:%S")
                db = get_db()
                actuals = get_sensor_values(ser)
                rh = actuals['actionable']['rh']
                co2 = actuals['actionable']['co2']
                o2 = actuals['other']['o2']
                airspeed = actuals['other']['airspeed']
                temperature = actuals['actionable']['temperature']
                print("Saving Data: ", datetimestr,temperature, rh, co2,o2,airspeed)
                db.execute(
                    'INSERT INTO envdata (datetime, temperature, rh, co2, o2, airspeed) VALUES (?,?,?,?,?,?)', (datetimestr, temperature, rh, co2, o2,airspeed ))
                db.commit()
        except Exception as e:
            print('Error Saving', e)
        time.sleep(600)
        
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
#    get_histdata()
    try:
        relay_setup()
        
        
        try:
            print("attempting to get ser")
            ser = serial.Serial('/dev/ttyACM1', 9600, write_timeout=1, timeout=1)
            
        except serial.SerialException:
            try:
                print("attempting to get ser 2")
                ser = serial.Serial('/dev/ttyACM0', 9600 ,write_timeout=1, timeout=1)
            except Exception as e:
                print(e)
        print("ser established", ser)   
        
    #    relayprocess = Process(target= repeat_loop)
    #    relayprocess.daemon = True
    #    relayprocess.start()
        
    #    savedataprocess = Process(target=save_loop)
    #    savedataprocess.daemon = True
    #    savedataprocess.start()

        relayprocess = threading.Thread(target=repeat_loop, args=[ser])
        relayprocess.daemon = True
        relayprocess.start()
        
        time.sleep(5) # waiting 5 seconds so serial calls dont overlap
        
        savedataprocess = threading.Thread(target=save_loop, args=[ser])
        savedataprocess.daemon = True
        savedataprocess.start()
        
    except KeyboardInterrupt:  
        GPIO.cleanup()  
