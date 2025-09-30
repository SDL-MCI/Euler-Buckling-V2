#include <Arduino.h>

#define SENSOR1_PIN A0 // Pin14
#define SENSOR2_PIN A1 // Pin15
#define SENSOR3_PIN A2 // Pin16
#define SENSOR4_PIN A3 // Pin17

float result1 = 0;
float result2 = 0;
float result3 = 0;
float result4 = 0;


void setup() {
  Serial.begin(9600);
  analogReadResolution(12);  // 0–4095
}

const float TEILERFAKTOR = 0.666; // Voltage divider factor (20k and 10k resistors)

const float ScaleFactor_1 = 9.90; // Scale factor for the sensor 1
const float Offset_V_1 = 0.7250; // Offset for the sensor 1 voltage

const float ScaleFactor_2 = 12.9049; // Scale factor for the sensor 2
const float Offset_V_2 = 0.48; // Offset for the sensor 2 voltage

const float ScaleFactor_3 = 37.95; // Scale factor for the sensor 3
const float Offset_V_3 = 0.52; // Offset for the sensor 3 voltage

void loop() {
  int raw1 = analogRead(SENSOR1_PIN); // Read raw ADC values
  int raw2 = analogRead(SENSOR2_PIN);
  int raw3 = analogRead(SENSOR3_PIN);


  float v1 = raw1 * 3.3 / 4095.0 / TEILERFAKTOR;// Convert to voltage
  float v2 = raw2 * 3.3 / 4095.0 / TEILERFAKTOR;
  float v3 = raw3 * 3.3 / 4095.0 / TEILERFAKTOR;
  

  float f1 = (v1 - Offset_V_1) * ScaleFactor_1; // Convert to Force
  float f2 = (v2 - Offset_V_2) * ScaleFactor_2;
  float f3 = (v3 - Offset_V_3) * ScaleFactor_3;

  // CSV-List for the Application
  // Force1, Force2, Force3
  Serial.print(f1, 2); Serial.print(",");
  Serial.print(f2, 2); Serial.print(",");
  Serial.print(f3, 2);
  Serial.println();

  delay(50); // Update-Rate
}
