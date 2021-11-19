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

    
    float temp_hum_val[2] = {0};
    StaticJsonDocument <200> doc;
    if (!dht.readTempAndHumidity(temp_hum_val)) {
      
      doc["O2"] = readO2Concentration();
      doc["H"] = temp_hum_val[0];
      doc["T"] = temp_hum_val[1];
      serializeJson(doc,Serial);
      Serial.println();
      
//      Serial.print("O2: ");
//      Serial.print(readO2Concentration());
//      Serial.print("%, ");
//      Serial.print("H: ");
//      Serial.print(temp_hum_val[0]);
//      Serial.print("%, ");
//      Serial.print("T: ");
//      Serial.print(temp_hum_val[1]);
//      Serial.println(" *C");

      delay(500);
    } else {
        Serial.println("Failed to get temperature and humidity value.");
    }
    // Reading temperature or humidity takes about 250 milliseconds!
    // Sensor readings may also be up to 2 seconds 'old' (its a very slow sensor)
    
    
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
