void setup() {
  Serial.begin(2400);
}

void loop() {
    Serial.write(67); // 67 decimal = 43 hex = C (ascii)
    delay(100);
}
