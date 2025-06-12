void setup() {
  Serial.begin(9600);
  while (!Serial) {
    ; // Wacht tot de seriële poort beschikbaar is
  }
  Serial.println("Seriële communicatie gestart");
}

void loop() {
  String input = "";
  if (Serial.available()) {
    input = Serial.readStringUntil('\n');  // Lees tot newline
    Serial.println("Ontvangen: " + input);

    // Split op komma's
    int idIndex = input.indexOf(',');
    int angleIndex = input.indexOf(',', idIndex + 1);

    if (idIndex > 0 && angleIndex > idIndex) {
      int markerID = input.substring(0, idIndex).toInt();
      float distance = input.substring(idIndex + 1, angleIndex).toFloat();
      float angle = input.substring(angleIndex + 1).toFloat();

      Serial.print("Ontvangen ID: ");
      Serial.println(markerID);
      Serial.print("Afstand: ");
      Serial.print(distance);
      Serial.print(" m, Hoek: ");
      Serial.print(angle);
      Serial.println(" graden");
    } else {
      Serial.println("Ongeldig dataformaat");
    }
  }
}
