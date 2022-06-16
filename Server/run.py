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
import schedule
# import relay module

app = create_app()

# Set up RELAY
def relay_setup():
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
    
    # Preset the relay as off
    GPIO.output(Relay_Ch1,GPIO.HIGH)
    GPIO.output(Relay_Ch2,GPIO.HIGH)
    GPIO.output(Relay_Ch3,GPIO.HIGH)
    
    relay_dict = {'temperature': {'ch': Relay_Ch1,'state':  False}, 'co2' : {'ch': Relay_Ch2,'state':  False}, 'rh' :  {'ch': Relay_Ch3,'state':  False}}
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
    
    
def compare_values(actualdict, targetdict):
#        print("check:",actualdict, targetdict)
        for i in targetdict:
            if actualdict[i] < targetdict[i]:
                relay_dict[i]['state'] = True
            else:
                relay_dict[i]['state'] = False
def co2_boost():
    relay_dict['co2']['state'] = True
    print("BOOSTING CO2")
    
def set_relays_off():
    for i in relay_dict:
        relay_dict[i]['state'] = False
        
def get_sensor_values(ser):   
    ser.reset_input_buffer()
    try:
        ser.write(b"GO\n")
        time.sleep(1)
        line = ser.readline().decode('utf-8').rstrip()
        if line == "GO" :
            data = ser.readline().decode('utf-8').rstrip()
            sensors_dict = json.loads(data)
        else:
            sensors_dict = {}          
    except Exception as e:
        print("EROOR: data stream")
        print(e)
        sensors_dict = {}
       # sensors_dict = {'actionable':{'temperature': 0, 'co2' : 0, 'rh' : 0}, 'other':{ 'airspeed': 0,'o2':0}}
    
    print("made it through sensor get")
    return sensors_dict

def get_targets():
    try:
        with app.app_context():
            db = get_db()
            querystr = 'SELECT temperature, rh, co2 FROM params LIMIT 1;'
            currentparams = db.execute('SELECT temperature, rh, co2 FROM params;').fetchall()
            rh = currentparams[0][1]
            temperature = currentparams[0][0]
            co2 = currentparams[0][2]
            current_params_dict = {'temperature': temperature, 'rh': rh, 'co2': co2}
            return current_params_dict
    except:
        print("Error, no targets set")
            
            
    
def repeat_loop(ser): # This function repeats itself every 15 seconds to update relays
    print("starting relay loop")
    while True:
        print(datetime.now())
        
        try:
            actuals = get_sensor_values(ser) #{'other': {'o2': 19.91613, 'airspeed': 0.588744}, 'actionable': {'temperature': 24.3, 'co2': 0, 'rh': 57}}
            
            targets = get_targets()
            #print("TARGETS", targets, "ACTUALS",actuals)
            compare_values(actuals['actionable'],targets)
            ## Shuttoff if fan fail
            if actuals['other']['airspeed'] < 6:
                set_relays_off()
                print("RELAYS OFF DUE TO LOW AIR SPEED")
            ## Run co2 boost schedule
            ##schedule.run_all(delay_seconds=0)
#            schedule.run_pending()
            update_relay()
            print("Updating Relay: ", relay_dict)
            now = datetime.now(get_localzone())
            datetimestr = now.strftime("%Y-%m-%d %H:%M:%S")
            rh = actuals["actionable"]["rh"]
            co2 = actuals['actionable']['co2']
            o2 = actuals['other']['o2']
            airspeed = actuals['other']['airspeed']
            temperature = actuals['actionable']['temperature']
            temp_relay = relay_dict['temperature']['state']
            rh_relay = relay_dict['rh']['state']
            co2_relay = relay_dict['co2']['state']
            
            print(rh, co2, o2, airspeed, temperature, temp_relay, rh_relay, co2_relay)
            
            
            try:
                with app.app_context():
                    db = get_db()
                    db.execute("DELETE FROM currentstates;") # 
                    db.commit()
                    db.execute(
                            'INSERT INTO currentstates (datetime, temperature, rh, co2, o2, airspeed,temp_relay, rh_relay, co2_relay) VALUES (?,?,?,?,?,?,?,?,?)',
                            (datetimestr, temperature, rh, co2, o2,airspeed,temp_relay, rh_relay, co2_relay  ))
                    db.commit()
                    print("relay table updated")
                    
                              
            except:
                print("couldnt update current readings and relays database")
                ## CODE HERE TO UPDATE ACTUALS TABLE
                ## CODE HERE TO UPDATE RELAYS TABLE
                #print("made it through relay loop")
                time.sleep(10)
        except:
            print("couldnt run relay control")

        
        time.sleep(7)
                

def save_loop(ser): # This loop runs every 5 mins to log data to graph 
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
                temp_relay = relay_dict['temperature']['state']
                rh_relay = relay_dict['rh']['state']
                co2_relay = relay_dict['co2']['state']
                print("Saving Data: ", datetimestr,temperature, rh, co2,o2,airspeed,temp_relay, rh_relay, co2_relay)
                db.execute(
                    'INSERT INTO envdata (datetime, temperature, rh, co2, o2, airspeed,temp_relay, rh_relay, co2_relay) VALUES (?,?,?,?,?,?,?,?,?)', (datetimestr, temperature, rh, co2, o2,airspeed,temp_relay, rh_relay, co2_relay  ))
                db.commit()
        except Exception as e:
            print('Error Saving', e)
        time.sleep(300)
        
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
        
        # Scheduling temporary co2 control
        print(datetime.now())
#        schedule.every().hour.do(co2_boost)
#        schedule.every().hour.at(":20").do(co2_boost)
#        schedule.every().hour.at(":42").do(co2_boost)
        
#        schedule.every().day.at("10:00").do(co2_boost)
#        print(schedule.next_run())
        # Setting up relay and saving threads
        
        relayprocess = threading.Thread(target=repeat_loop, args=[ser])
        relayprocess.daemon = True
        relayprocess.start()
        
        time.sleep(5) # waiting 5 seconds so serial calls dont overlap
        
        savedataprocess = threading.Thread(target=save_loop, args=[ser])
        savedataprocess.daemon = True
        savedataprocess.start()
        
    except KeyboardInterrupt:  
        GPIO.cleanup()  
