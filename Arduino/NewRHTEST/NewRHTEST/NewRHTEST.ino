
#include <Arduino.h>
#include <Wire.h>
#include "SHT31.h"
#include <DHT.h>

SHT31 sht31 = SHT31();
#define DHTTYPE DHT11   // DHT 11
#define DHTPIN 2     // what pin we're connected to（DHT10 and DHT20 don't need define it）
DHT dht(DHTPIN, DHTTYPE);

void setup() {
    Serial.begin(9600);
    while (!Serial);
    Serial.println("begin...");
    Wire.begin();
    sht31.begin();
    dht.begin();
}

void loop() {
    float temp = sht31.getTemperature();
    float hum = sht31.getHumidity();
    float temp_hum_val[2] = {0};
    float hum2 = temp_hum_val[0];
    float temp2= temp_hum_val[1];

    if (!dht.readTempAndHumidity(temp_hum_val)) {
      Serial.print("Temp = ");
      Serial.print(temp);
      Serial.print(" ");
      Serial.println( temp2); //The unit for  Celsius because original arduino don't support speical symbols
      Serial.print("Hum = ");
      Serial.print(hum);
      Serial.print(" ");
      Serial.println(hum2);
      Serial.println();
      delay(1000);
     } else {
        debug.println("Failed to get temprature and humidity value.");
    }
}
