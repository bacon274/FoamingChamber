// O2, (T, RH), Sensor Code
// Note:
// 1. It need about about 5-10 minutes to preheat the sensor
// 2. modify VRefer if needed
// 3. Include temperature and humidity sensor library 
//#include <DHT.h>

#include <ArduinoJson.h>
#include <LiquidCrystal_I2C.h>
#include "SHT31.h"
#include <Arduino.h>

// Define Humidity sensor parameters
//#define DHTTYPE DHT11   // DHT 11
//#define DHTPIN 2     // what pin we're connected to（DHT10 and DHT20 don't need define it）
//DHT dht(DHTPIN, DHTTYPE);

// New Rh

SHT31 sht31 = SHT31();

// O2 Sensor parameters
const float VRefer = 3.3;       // voltage of adc reference
const int pinAdc   = A0;

// Anemometer
const int analogPinForRV = A3;  
const int analogPinForTMP = A2; 
const float zeroWindAdjustment =  .2; // negative numbers yield smaller wind speeds and vice versa. 

// NEW RH t9602
const int analogPinForRH = A0;  
const int analogPinForTemp = A1; 


// DECLARING VARIABLES:
int TMP_Therm_ADunits;  //temp termistor value from wind sensor
float RV_Wind_ADunits;    //RV output from wind sensor 
float RV_Wind_Volts; 
float Temp_ADunits; // T9602 RH and T
float RH_ADunits; // T9602 RH and T
float VDD = 5.0; 
unsigned long lastMillis;
int TempCtimes100;
float zeroWind_ADunits;
float zeroWind_volts;
float WindSpeed_MPH;

// LCD 
LiquidCrystal_I2C lcd(0x27, 16, 2); // set the LCD address to 0x27 for a 16 chars and 2 line display

// CO2 Sensor 
const int rx_pin = 19; //Serial rx pin no
const int tx_pin = 18; //Serial tx pin no
const int buf_len = 9; // Length of buffer
uint8_t getppm[buf_len] = {0xff, 0x01, 0x86, 0x00, 0x00, 0x00, 0x00, 0x00,0x79}; // Command buffer to send
uint8_t response[buf_len] = {0, 0, 0, 0, 0, 0, 0,0,0};
unsigned long startTime; // time warm-up began
void setup() {

    Serial.begin(9600);
    Serial1.begin(9600); // Initialise co2 sensor serial connection
    Wire.begin(); // initialise  i2c
    //dht.begin();
    sht31.begin();
    lcd.init();  //initialize the lcd
    lcd.backlight();  //open the backlight
    lcd.setCursor(1,0);
    startTime = millis();
    
    lcd.print("Starting up...");
    
}

void loop(){
      

    if (Serial.available() > 0) {
      String data = Serial.readStringUntil('\n');
      Serial.println(data);
      if (data=="GO"){
        StaticJsonDocument <200> doc;
        doc["other"]["o2"] = 0.0;
        doc["actionable"]["rh"] =readRH_T9602();
        doc["actionable"]["temperature"] = readT_T9602();
        doc["other"]["airspeed"] = readAirSpeed();
        doc["actionable"]["co2"] = readCo2Concentration();
        serializeJson(doc,Serial);
        Serial.println();

        String lcdString =  "T: " + String(float(doc["actionable"]["temperature"]),1) + "C" 
        + " RH:"+ String(float(doc["actionable"]["rh"]),0)+ "%";
       
        String lcdString2 = "CO2:" + String(float(doc["actionable"]["co2"]),1)+"%"; 
        
        lcd.clear();
        lcd.setCursor(0,0);
        lcd.print(lcdString);
        lcd.setCursor(0,1);
        lcd.print(lcdString2);

        
        } else {
            Serial.println("Failed to get sensor values.");
        }
        
        
      }
      

      
   delay(1);
    
    
}


float readRH_T9602(){
  RH_ADunits = analogRead(analogPinForTemp); // Analog reading between 0-1023 
  float RH_V = 4.7*(RH_ADunits/1023);
  float RH_perc = (RH_V*100.0)/4.7; 
//
//  Serial.print("RH_AD: ");
//  Serial.println(RH_ADunits);
//  Serial.print("RH_V: ");
//  Serial.println(RH_V);
//  Serial.print("RH_perc: ");
//  Serial.println(RH_perc);


  return RH_perc;

  }
float readT_T9602() {
  Temp_ADunits = analogRead(analogPinForRH);
  float Temp_V = 4.7*(Temp_ADunits/1023);
  float T_celcius = ((Temp_V/4.7)-0.2424)*165;
  
//  Serial.print("T_AD: ");
//  Serial.println(Temp_ADunits);
//  Serial.print("T_V: ");
//  Serial.println(Temp_V);
//  Serial.print("T_celcius: ");
//  Serial.println(T_celcius);
 
  return T_celcius;
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
  float co2percent;
  unsigned long co2;
  
  if ((millis()-startTime)<0){
    return -1; 
  }
  else{
    Serial1.write(getppm, buf_len);
    Serial1.flush();
    delay(500);
    while (Serial1.available()<=0){
//      Serial.print("Buffer available: ");
//      Serial.println(Serial1.available());
      delay(1000);
    }
    while (Serial1.available()> 0){
//      Serial.print("Buffer available: ");
//      Serial.println(Serial1.available());
      Serial1.readBytes(response,buf_len);
    }
    if (response[0] == 0xff && response[1] == 0x86 && checksum(response) == response[8]){
        co2 = (long) response[2]*256L + (long) response[3];
        
      }else{
       // Serial.println(checksum(response));
//        Serial.print("buffer checksum: ");
//        Serial.println(response[buf_len-1]);
        co2 = -1;}
    
    float co2ppm = (long) response[2]*256L + (long) response[3];
    Serial.print(co2ppm);
    co2percent = co2ppm/10000;
//    Serial.println(co2);
    return co2percent;
  }
}

uint8_t checksum(uint8_t com[]) {
  uint8_t sum = com[1]+com[2]+com[3]+com[4]+com[5]+com[6]+com[7];
  sum = 0xff - sum + 0x01;
//  Serial.print("checksum calc: ");
//  Serial.println(sum);
//  Serial.print("checksum val: ");
//  Serial.println(com[8]);
  return sum;
}
