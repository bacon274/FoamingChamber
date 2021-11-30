// O2, (T, RH) Sensor Code
// Note:
// 1. It need about about 5-10 minutes to preheat the sensor
// 2. modify VRefer if needed
// 3. Include temperature and humidity sensor library 
#include <DHT.h>
#include <ArduinoJson.h>

// Define Humidity sensor parameters
#define DHTTYPE DHT11   // DHT 11
#define DHTPIN 2     // what pin we're connected to（DHT10 and DHT20 don't need define it）
DHT dht(DHTPIN, DHTTYPE);

// O2 Sensor parameters
const float VRefer = 3.3;       // voltage of adc reference
const int pinAdc   = A0;
// Anemometer
const int analogPinForRV = A3;  
const int analogPinForTMP = A2; 
const float zeroWindAdjustment =  .2; // negative numbers yield smaller wind speeds and vice versa. 

// DECLARING VARIABLES:
int TMP_Therm_ADunits;  //temp termistor value from wind sensor
float RV_Wind_ADunits;    //RV output from wind sensor 
float RV_Wind_Volts;
unsigned long lastMillis;
int TempCtimes100;
float zeroWind_ADunits;
float zeroWind_volts;
float WindSpeed_MPH;

// Debugging stuff, not sure if needed?
//#if defined(ARDUINO_ARCH_AVR)
//    #define debug  Serial
//
//#elif defined(ARDUINO_ARCH_SAMD) ||  defined(ARDUINO_ARCH_SAM)
//    #define debug  SerialUSB
//#else
//    #define debug  Serial
//#endif

void setup() {

    Serial.begin(9600);
//    Serial.println("DHTxx test!");
    Wire.begin(); // initialise  i2c
    dht.begin();
    
}

void loop(){
    
    if (Serial.available() > 0) {
      String data = Serial.readStringUntil('\n');
      Serial.println(data);
      if (data=="GO"){
        float temp_hum_val[2] = {0};
        StaticJsonDocument <200> doc;
        if (!dht.readTempAndHumidity(temp_hum_val)) {
          doc["o2"] = readO2Concentration();
          doc["rh"] = temp_hum_val[0];
          doc["temperature"] = temp_hum_val[1];
          doc["airspeed"] = readAirSpeed();
          doc["co2"] = readCo2Concentration();
          serializeJson(doc,Serial);
          Serial.println();
          delay(500);
        } else {
            Serial.println("Failed to get sensor values.");
        }
        
      }
      
  }
    
    
}

float readAirSpeed() {
  
   TMP_Therm_ADunits = analogRead(analogPinForTMP);
   RV_Wind_ADunits = analogRead(analogPinForRV);
   RV_Wind_Volts = (RV_Wind_ADunits *  0.0048828125);

    TempCtimes100 = (0.005 *((float)TMP_Therm_ADunits * (float)TMP_Therm_ADunits)) - (16.862 * (float)TMP_Therm_ADunits) + 9075.4;  

    zeroWind_ADunits = -0.0006*((float)TMP_Therm_ADunits * (float)TMP_Therm_ADunits) + 1.0727 * (float)TMP_Therm_ADunits + 47.172;  //  13.0C  553  482.39

    zeroWind_volts = (zeroWind_ADunits * 0.0048828125) - zeroWindAdjustment;  

  // This from a regression from data in the form of 
  // Vraw = V0 + b * WindSpeed ^ c
  // V0 is zero wind at a particular temperature
  // The constants b and c were determined by some Excel wrangling with the solver.
  
  WindSpeed_MPH =  pow(((RV_Wind_Volts - zeroWind_volts) /.2300) , 2.7265);   
  return WindSpeed_MPH;
}

float readO2Vout()
{
    long sum = 0;
    for(int i=0; i<32; i++)
    {
        sum += analogRead(pinAdc);
    }
 
    sum >>= 5;
 
    float MeasuredVout = sum * (VRefer / 1023.0);
    return MeasuredVout;
}

float readO2Concentration()
{
    // Vout samples are with reference to 3.3V
    float MeasuredVout = readO2Vout();
 
    //float Concentration = FmultiMap(MeasuredVout, VoutArray,O2ConArray, 6);
    //when its output voltage is 2.0V,
    float Concentration = MeasuredVout * 0.21 / 2.0;
    float Concentration_Percentage=Concentration*100;
    return Concentration_Percentage;
}

float readCo2Concentration(){
  /// INSERT CODE WITH CO2 SENSOR
  return 0;
}
