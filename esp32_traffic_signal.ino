#define RED_LED 25
#define GREEN_LED 26
#define BUZZER 23

// Keep false until the buzzer transistor circuit is installed.
// Change to true after completing the buzzer wiring.
const bool BUZZER_INSTALLED = false;

void redSignal() {
  digitalWrite(RED_LED, HIGH);
  digitalWrite(GREEN_LED, LOW);
  digitalWrite(BUZZER, LOW);
}

void setup() {
  Serial.begin(115200);

  pinMode(RED_LED, OUTPUT);
  pinMode(GREEN_LED, OUTPUT);
  pinMode(BUZZER, OUTPUT);

  // Default traffic state
  redSignal();

  Serial.println("ANPR TRAFFIC SIGNAL READY");
}

void loop() {

  if (Serial.available() > 0) {

    String command = Serial.readStringUntil('\n');
    command.trim();

    if (command == "TRIGGER") {

      Serial.println("VEHICLE RECORD RECEIVED");

      // Red OFF
      digitalWrite(RED_LED, LOW);

      // Buzzer ON for 3.5 seconds
      if (BUZZER_INSTALLED) {
        digitalWrite(BUZZER, HIGH);
      }

      delay(3500);

      // Buzzer OFF
      digitalWrite(BUZZER, LOW);

      // Green ON for 2.5 seconds
      digitalWrite(GREEN_LED, HIGH);
      delay(2500);

      // Green OFF, Red ON
      digitalWrite(GREEN_LED, LOW);
      digitalWrite(RED_LED, HIGH);

      Serial.println("TRAFFIC SIGNAL RESET");
    }
  }
}