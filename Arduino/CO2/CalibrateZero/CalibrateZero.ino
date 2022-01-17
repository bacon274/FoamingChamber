const int rx_pin = 19; //Serial rx pin no
const int tx_pin = 18; //Serial tx pin no

const int buf_len = 9; // Length of buffer
uint8_t getppm[buf_len] = {0xff, 0x01, 0x86, 0x00, 0x00, 0x00, 0x00, 0x00,0x79}; // Command buffer to send
uint8_t calibratezero[buf_len] = {0xff, 0x01, 0x87, 0x00, 0x00, 0x00, 0x00, 0x00,0x78};
uint8_t selfcaloff[buf_len] = {0xff, 0x01, 0x79, 0x00, 0x00, 0x00, 0x00, 0x00,0x86};
uint8_t setrange[buf_len] = {0xff, 0x01, 0x99, 0x00, 0x00, 0x00, 0xFF, 0xDC, 0x8B};

int incomingByte = 0; // for incoming serial data
uint8_t response[buf_len] = {0, 0, 0, 0, 0, 0, 0,0,0};

int i;

void setup() {
  Serial.begin(9600);
  Serial1.begin(9600);
  Serial.println("Warming up sensor");
  // delay(180000);
  Serial.println("Sensor warm");
  
  
 
}

void loop(){
  Serial.println("Writing zero point calibration");
  
  Serial1.write(setrange, buf_len);
  Serial1.flush();
  delay(3000);
  Serial.println("Written zero point calibration");

}
