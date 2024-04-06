#include <Arduino.h>
#include <Wire.h>

const int potPin = A0;
const int sensorPin = A3;

const int TEST = 0;
const int RUN = 1;
const int STOP = 2;

int pot = 0;
uint16_t sensor = 0;
int actuator = 0;
int flag = 0;

const int inSize = 3;
byte inBuffer[inSize];

const int outSize = 3;
byte outBuffer[outSize];

const byte MCP4725 = (0x60);

void setup() {
  // Initialize serial communication
  Serial.begin(115200);
  Wire.begin();

  analogReference(EXTERNAL);
}

void send() {
  Serial.write(outBuffer, outSize);
}

void receive() {
  Serial.readBytes(inBuffer, inSize);
  flag = inBuffer[0];
  actuator = (inBuffer[1] << 8) + inBuffer[2];
}

void sensorRead() {
  pot = analogRead(potPin);
  sensor = analogRead(sensorPin);
}

void actuatorWrite(uint16_t DAClevel) {
  Wire.beginTransmission(MCP4725); 					//addressing
  Wire.write(0x40); 								// write dac(DAC and EEPROM is 0x60)
  uint8_t firstbyte=(DAClevel>>4);					//(0,0,0,0,0,0,0,0,D11,D10,D9,D8,D7,D6,D5,D4) of which only the 8 LSB's survive
  DAClevel = DAClevel << 12;  						//(D3,D2,D1,D0,0,0,0,0,0,0,0,0,0,0,0,0)
  uint8_t secndbyte=(DAClevel>>8);					//(0,0,0,0,0,0,0,0,D3,D2,D1,D0,0,0,0,0) of which only the 8 LSB's survive.
  Wire.write(firstbyte); //first 8 MSB's
  Wire.write(secndbyte); //last 4 LSB's
  Wire.endTransmission();
}

void setOutBuffer(int v1, int v2) {
  outBuffer[0] = ((v1 >> 4) & 0xF0) + (v2 >> 8);
  outBuffer[1] = v1 & 0xFF;
  outBuffer[2] = v2 & 0xFF;
}

void loop() {
  if (Serial.available() > 0){
    receive();
    switch(flag) {
      case TEST:
        {
          setOutBuffer(actuator * 2, actuator * 4);

          break;
        }
      case RUN:
        {
          actuatorWrite(actuator);
          sensorRead();
          setOutBuffer(pot, sensor);

          break;
        }

      case STOP:
        actuatorWrite(0);

        break;
    }

    send();
  }
}
