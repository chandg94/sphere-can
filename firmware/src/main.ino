/*
  Teensy relay controller for SPHERE CAN testbed

  Serial protocol:
    <ecu>:ON\n
    <ecu>:OFF\n

  Example:
    cummins:ON
    ddec:OFF
*/

struct Relay {
  const char* name;
  uint8_t pin;
  bool state;
};

// Define relays
Relay relays[] = {
  {"cummins", 6, false},
  {"ddec",    5, false},
  {"bendix",  7, false},
};

const size_t NUM_RELAYS = sizeof(relays) / sizeof(relays[0]);

String inputLine;

void setup() {
  Serial.begin(115200);
  while (!Serial && millis() < 3000) {
    // wait briefly for host
  }

  for (size_t i = 0; i < NUM_RELAYS; i++) {
    pinMode(relays[i].pin, OUTPUT);
    digitalWrite(relays[i].pin, LOW);  // OFF by default
  }

  Serial.println("READY");
}

void loop() {
  while (Serial.available()) {
    char c = Serial.read();

    if (c == '\n') {
      processCommand(inputLine);
      inputLine = "";
    } else if (c != '\r') {
      inputLine += c;
    }
  }
}

void processCommand(const String& cmd) {
  int sep = cmd.indexOf(':');
  if (sep < 0) {
    Serial.println("ERR format");
    return;
  }

  String name = cmd.substring(0, sep);
  String action = cmd.substring(sep + 1);

  name.toLowerCase();
  action.toUpperCase();

  for (size_t i = 0; i < NUM_RELAYS; i++) {
    if (name == relays[i].name) {
      if (action == "ON") {
        digitalWrite(relays[i].pin, HIGH);
        relays[i].state = true;
        Serial.println(name + ":ON");
        return;
      } 
      else if (action == "OFF") {
        digitalWrite(relays[i].pin, LOW);
        relays[i].state = false;
        Serial.println(name + ":OFF");
        return;
      } 
      else {
        Serial.println("ERR action");
        return;
      }
    }
  }

  Serial.println("ERR unknown");
}
