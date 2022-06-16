# FoamingChamber
 The control system for the foam chamber. 
 Web server hosted on the raspberry pi, controlling electrical components via relay board. Sensor 
## Notes: 
- serial adress for arduino: /dev/ttyACM0cd

## Dependencies:
### Raspberry Pi 
- python3 -m pip install pyserial
- Flask 
- pandas
- python-dateutil
- tzlocal
- gunicorn 
- systemd

### Arduino:
- DHT sensor library 
- ArduinoJson


## To run: 
### Flask Web server: python -m flask run (in the Server Directory)
