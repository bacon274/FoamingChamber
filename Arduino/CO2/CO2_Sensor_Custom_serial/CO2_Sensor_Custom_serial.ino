
const int rx_pin = 19; //Serial rx pin no
const int tx_pin = 18; //Serial tx pin no

const int buf_len = 9; // Length of buffer
uint8_t getppm[buf_len] = {0xff, 0x01, 0x86, 0x00, 0x00, 0x00, 0x00, 0x00,0x79}; // Command buffer to send
uint8_t setrange[buf_len] = {0xff, 0x01, 0x99, 0x00, 0x00, 0x00, 0xEA, 0x60, 0x1C};
int incomingByte = 0; // for incoming serial data
int i;
void setup() {
  Serial.begin(9600);
  Serial1.begin(9600);
  Serial.println("Warming up sensor");
  // delay(180000);
  Serial.println("Sensor warm");
  checksum(setrange);
}

void loop() {
  uint8_t response[buf_len] = {0, 0, 0, 0, 0, 0, 0,0,0};
  long co2;
  float co2perc;
  
  Serial.println("Writing get ppm Command");
  Serial1.write(getppm, buf_len);
  Serial1.flush();
  delay(500);
  
  while (Serial1.available()<=0){
      Serial.print("Buffer available: ");
      Serial.println(Serial1.available());
      delay(1000);
  }
   while (Serial1.available()> 0){
      Serial.print("Buffer available: ");
      Serial.println(Serial1.available());
      Serial1.readBytes(response,buf_len);
      Serial.print("Response Bytes: ");
      
      for (i=0; i<buf_len; i++){
         Serial.print(response[i]);
         Serial.print(" ");
      }
      Serial.println();
      if (response[0] == 0xff && response[1] == 0x86 && checksum(response) == response[8]){
//        long r2 = (long) response[2];
//        long 
        co2 = (long) response[2]*256L + (long) response[3];
        co2perc = (float) co2/10000;
      }else{
       // Serial.println(checksum(response));
        Serial.print("buffer checksum: ");
        Serial.println(response[buf_len-1]);
        co2 = -1;}
      
      
      Serial.print("co2 concentration: " );
      Serial.println(co2);
      Serial.println(co2perc);
     
      
//      incomingByte = Serial.read();
//      Serial.print("I received: ");
//      Serial.println(incomingByte, DEC);
      delay(500);
  }
  
  delay(3000);
}

uint8_t checksum(uint8_t com[]) {
  uint8_t sum = com[1]+com[2]+com[3]+com[4]+com[5]+com[6]+com[7];
  sum = 0xff - sum + 0x01;
  Serial.print("checksum calc: ");
  Serial.println(sum);
  Serial.print("checksum val: ");
  Serial.println(com[8]);
  return sum;
}
