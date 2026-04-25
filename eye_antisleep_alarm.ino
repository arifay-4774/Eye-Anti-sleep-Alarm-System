#include <SoftwareSerial.h>

SoftwareSerial BT(10, 11); // RX, TX

int BUZZER = 8;

void setup() {
  pinMode(BUZZER, OUTPUT);
  digitalWrite(BUZZER, LOW);
  BT.begin(9600);
  Serial.begin(9600);
}

void loop() {
  if (BT.available()) {
    char cmd = BT.read();
    Serial.println(cmd);

    if (cmd == 'A') {       // ALARM → buzzer ON
      digitalWrite(BUZZER, HIGH);
    } else if (cmd == 'S') { // STOP → buzzer OFF
      digitalWrite(BUZZER, LOW);
    }
  }
}