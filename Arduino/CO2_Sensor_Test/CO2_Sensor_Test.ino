#include <SoftwareSerial.h>
#include <Wire.h>
#include <SPI.h>

// Setting up serial to uart sensor
SoftwareSerial mySerial(0, 1); // RX, TX



byte mhzCmdMeasurementRange1000[9] = {0xFF,0x01,0x99,0x00,0x00,0x00,0x03,0xE8,0x7B};
byte mhzCmdMeasurementRange2000[9] = {0xFF,0x01,0x99,0x00,0x00,0x00,0x07,0xD0,0x8F};
byte mhzCmdMeasurementRange3000[9] = {0xFF,0x01,0x99,0x00,0x00,0x00,0x0B,0xB8,0xA3};
byte mhzCmdMeasurementRange5000[9] = {0xFF,0x01,0x99,0x00,0x00,0x00,0x13,0x88,0xCB};
byte mhzCmdReset[9] = {0xFF,0x01,0x8d,0x00,0x00,0x00,0x00,0x00,0x72};
byte mhzCmdCalibrateZero[9] = {0xFF,0x01,0x87,0x00,0x00,0x00,0x00,0x00,0x78};
byte mhzCmdABCEnable[9] = {0xFF,0x01,0x79,0xA0,0x00,0x00,0x00,0x00,0xE6}; //enable
//unsigned char response[9]; 
byte response[9];

unsigned long u = 0;
unsigned long th, tl,ppmMHZ19, s, oldppmMHZ19, tvoc, tpwm, p1, p2, ppm2, ppm3 = 0;

void setup() {
  Serial.begin(9600);
  delay(1000)
  mySerial.begin(9600); 
  Serial.println("Setting up MH-Z19 to 5000ppm")
  mySerial.write(mhzCmdMeasurementRange5000,9);
  delay(200);
  mySerial.readBytes(response, 9);
  unsigned int responseV1 = (unsigned int) response[0];
  unsigned int responseV2 = (unsigned int) response[1];
  unsigned int responseHigh = (unsigned int) response[2];
  unsigned int responseLow = (unsigned int) response[3];
  unsigned int temperatureRaw = (unsigned int) response[4];
  unsigned int mhzRespS = (unsigned int) response[5];
  unsigned int mhzRespUHigh = (unsigned int) response[6];
  unsigned int mhzRespULow = (unsigned int) response[7];
  unsigned int responseV9 = (unsigned int) response[7];

  Serial.println("Booting MH-Z19");

}

void loop() {
  oldppmMHZ19 = ppmMHZ19;
  mySerial.write(cmd,9);
  delay(200);
  mySerial.readBytes(response, 9);
  unsigned int responseHigh = (unsigned int) response[2];
  unsigned int responseLow = (unsigned int) response[3];
  unsigned int temperatureRaw = (unsigned int) response[4];
  unsigned int mhzRespUHigh = (unsigned int) response[6];
  unsigned int mhzRespULow = (unsigned int) response[7];

  temperatureRaw = (unsigned int) response[4];
  temperatureCorrected = temperatureRaw - 40;
  ppmMHZ19 = (256*responseHigh)+responseLow;
  u = (256*mhzRespUHigh) + mhzRespULow;
  if (u==15000)Serial.println("usiech");
  delay(200);
  Serial.print(" ");
  Serial.println(ppmMHZ19);

}
