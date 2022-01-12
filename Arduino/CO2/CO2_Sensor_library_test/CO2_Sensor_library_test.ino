#include <MHZ16_uart.h>
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x27, 16, 2); // set the LCD address to 0x27 for a 16 chars and 2 line display

const int rx_pin = 19; //Serial rx pin no
const int tx_pin = 18; //Serial tx pin no

MHZ16_uart mhz16 = MHZ16_uart();
//MHZ16_uart mhz16;

void setup() {
   Wire.begin(); // initialise  i2c
//   lcd.init();  //initialize the lcd
//   lcd.backlight();  //open the backlight
//   lcd.setCursor(1,0);
   Serial.begin(9600);
   mhz16.begin(rx_pin, tx_pin);
//   lcd.print("MH-Z19 is warming up now.");
   Serial.print("MH-Z19 is warming up now.");
   delay(180000); //
//   lcd.print("Finished Warming");
   Serial.print("Finished Warming");
}

void loop() {
  int co2ppm = mhz16.getPPM();
  Serial.println(co2ppm);
//  lcd.clear();
//  lcd.setCursor(0,0);
//  lcd.print(co2ppm);
  

  delay(5000);

}
