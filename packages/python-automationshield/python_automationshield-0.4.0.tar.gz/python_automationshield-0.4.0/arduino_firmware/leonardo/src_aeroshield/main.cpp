#include <Arduino.h>
#include <AS5600_AS.h>

const int potPin = A3;
const int actuatorPin = 5;

const int TEST = 0;
const int RUN = 1;
const int STOP = 2;

const int inSize = 2;
byte inBuffer[inSize];

const int outSize = 3;
byte outBuffer[outSize];

AS5600 as5600;


void setup() {
  // Initialize serial communication
  Serial.begin(115200);
  Wire.begin();
  as5600.setWirePtr(&Wire);
  as5600.begin();
}


void receive() {
  Serial.readBytes(inBuffer, inSize);
}


void send() {
  Serial.write(outBuffer, outSize);
}


void loop() {
  if (Serial.available() > 0){
    receive();
    switch(inBuffer[0]) {
      case TEST:
        {
          int r1 = inBuffer[1] * 2;
          int r2 = inBuffer[1] * 4;

          outBuffer[0] = ((r1 >> 4) & 0xF0) + (r1 >> 8);
          outBuffer[1] = r1 & 0xFF;
          outBuffer[2] = r2 & 0xFF;

          break;
        }
      case RUN:
        {
          analogWrite(actuatorPin, inBuffer[1]);

          int pot = analogRead(potPin);
          uint16_t angle = as5600.rawAngle();

          outBuffer[0] = ((pot >> 4) & 0xF0) + (angle >> 8);
          outBuffer[1] = pot & 0xFF;
          outBuffer[2] = angle & 0xFF;

          break;
        }

      case STOP:
        analogWrite(actuatorPin, 0);

        break;
    }
    send();
  }
}
