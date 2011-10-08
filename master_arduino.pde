// Pin configuration:
// Right button - Brown Wire
int RIGHT_PIN = 13;
// Left button - Green Wire
int LEFT_PIN = 12;
// Up button - White Wire
int UP_PIN = 11;
// Down button - Blue Wire
int DOWN_PIN = 10;
// A button - Orange Wire
int A_PIN = 9;
// B button - Gray Wire
int B_PIN = 8;

// last byte read from serial port
int readByte = 0;

void setup()
{
    Serial.begin(9600);
    // set one output pin for each possible command
    // set initial state as inactive, that is, HIGH output
    pinMode(LEFT_PIN, OUTPUT);  digitalWrite(LEFT_PIN, HIGH);
    pinMode(RIGHT_PIN, OUTPUT); digitalWrite(RIGHT_PIN, HIGH);
    pinMode(DOWN_PIN, OUTPUT);  digitalWrite(DOWN_PIN, HIGH);
    pinMode(UP_PIN, OUTPUT);    digitalWrite(UP_PIN, HIGH);
    pinMode(A_PIN, OUTPUT);     digitalWrite(A_PIN, HIGH);
    pinMode(B_PIN, OUTPUT);     digitalWrite(B_PIN, HIGH);
}

void loop()
{
  // since the voltage drops to zero when a button is pressed,
  // in order to send "A button" command, its wire output should be 
  // set to low.
  if (Serial.available() > 0)
  {
    readByte = Serial.read();
    switch (readByte)
    {
      case 1: digitalWrite(LEFT_PIN, LOW); break;
      case 2: digitalWrite(LEFT_PIN, HIGH); break;
      case 3: digitalWrite(RIGHT_PIN, LOW); break;
      case 4: digitalWrite(RIGHT_PIN, HIGH); break;
      case 5: digitalWrite(DOWN_PIN, LOW); break;
      case 6: digitalWrite(DOWN_PIN, HIGH); break;
      case 7: digitalWrite(UP_PIN, LOW); break;
      case 8: digitalWrite(UP_PIN, HIGH); break;
      case 9: digitalWrite(A_PIN, LOW); break;
      case 10: digitalWrite(A_PIN, HIGH); break;
      case 11: digitalWrite(B_PIN, LOW); break;
      case 12: digitalWrite(B_PIN, HIGH); break;      
    }
  }  
}
