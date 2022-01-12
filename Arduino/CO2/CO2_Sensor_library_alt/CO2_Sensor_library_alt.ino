#include <MHZ16_uart.h>



//Select 2 digital pins as SoftwareSerial's Rx and Tx. For example, Rx=2 Tx=3
const int rx_pin = 19; //Serial rx pin no
const int tx_pin = 18; //Serial tx pin no

MHZ16_uart mySensor(rx_pin,tx_pin);
 
void setup()
{
  Serial.begin(9600);
 
  mySensor.begin(rx_pin,tx_pin); 
}
 
 
void loop() 
{
  if ( !mySensor.isWarming())
  {
    Serial.print("CO2 Concentration is ");
    Serial.print(mySensor.getPPM());
    
    Serial.println("ppm");
  }
  else
{
    Serial.println("isWarming");
  }
   
  delay(10000);
}
