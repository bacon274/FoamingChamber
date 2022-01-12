
const int rx_pin = 19; //Serial rx pin no
const int tx_pin = 18; //Serial tx pin no

const int buf_len = 9; // Length of buffer
uint8_t getppm[buf_len] = {0xff, 0x01, 0x86, 0x00, 0x00, 0x00, 0x00, 0x00,0x79}; // Command buffer to send
//uint8_t calibratezero[buf_len] = 
int incomingByte = 0; // for incoming serial data
int i;
void setup() {
  Serial.begin(9600);
  Serial1.begin(9600);
  Serial.println("Warming up sensor");
  // delay(180000);
  Serial.println("Sensor warm");
}

void loop() {
  uint8_t response[buf_len] = {0, 0, 0, 0, 0, 0, 0,0,0};
  int co2;
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
      if (response[0] == 0xff && response[1] == 0x86 && checksum(response) == response[buf_len-1]){
        co2 = response[2]*256 + response[3];
      }else{
       // Serial.println(checksum(response));
        Serial.print("buffer checksum: ");
        Serial.println(response[buf_len-1]);
        co2 = -1;}
      
      
      Serial.print("co2 concentration: " );
      Serial.println(co2);
     
      
//      incomingByte = Serial.read();
//      Serial.print("I received: ");
//      Serial.println(incomingByte, DEC);
      delay(500);
  }
  
  delay(3000);
}

uint8_t checksum(uint8_t com[]) {
  uint8_t sum = 0x00;
  for (int i = 1; i < buf_len; i++) {
    sum += com[i];
    Serial.print(com[i]);
    Serial.print("+=");
    Serial.println(sum);
  }
  sum = 0xff - sum + 0x01;
  Serial.print("checksum calc: ");
  Serial.println(sum);
}
