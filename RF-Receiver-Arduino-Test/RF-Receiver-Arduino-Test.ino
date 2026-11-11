// SPDX-FileCopyrightText: 2026 TinkeringTech LLC
//
// SPDX-License-Identifier: MIT
//
// ScoutMakes RF Remote Receiver test code (Arduino, I2C / PCA9536)

#include <Wire.h>

const uint8_t PCA9536_ADDR = 0x41;
const uint8_t REG_INPUT = 0x00;   // Input Port register
const uint8_t REG_CONFIG = 0x03;  // Configuration register (1 = input)
const bool ACTIVE_HIGH = true;    // receiver outputs go high when a button is pressed

const char BUTTON_NAMES[4] = {'A', 'B', 'C', 'D'};  // bit 0..3 -> fob button

uint8_t last = 0;

void writeReg(uint8_t reg, uint8_t value) {
  Wire.beginTransmission(PCA9536_ADDR);
  Wire.write(reg);
  Wire.write(value);
  Wire.endTransmission();
}

int readReg(uint8_t reg) {
  Wire.beginTransmission(PCA9536_ADDR);
  Wire.write(reg);
  if (Wire.endTransmission(false) != 0) return -1;
  if (Wire.requestFrom(PCA9536_ADDR, (uint8_t)1) != 1) return -1;
  return Wire.read();
}

void setup() {
  Serial.begin(115200);
  while (!Serial && millis() < 3000) {}
  Wire.begin();  // Use Wire1 on boards whose Qwiic/STEMMA QT port is on a second bus

  Wire.beginTransmission(PCA9536_ADDR);
  if (Wire.endTransmission() != 0) {
    Serial.println("RF Remote Receiver not found at 0x41 - check the cable");
    while (true) delay(1000);
  }

  writeReg(REG_CONFIG, 0x0F);  // IO0-IO3 as inputs
  Serial.println("RF Remote Receiver ready - press a button on the fob");
}

void loop() {
  int raw = readReg(REG_INPUT);
  if (raw < 0) {
    delay(50);
    return;
  }

  uint8_t state = raw & 0x0F;
  if (!ACTIVE_HIGH) state = ~state & 0x0F;

  if (state != last) {
    for (uint8_t i = 0; i < 4; i++) {
      uint8_t mask = 1 << i;
      if ((state & mask) && !(last & mask)) {
        Serial.print("Button "); Serial.print(BUTTON_NAMES[i]); Serial.println(" pressed");
      } else if (!(state & mask) && (last & mask)) {
        Serial.print("Button "); Serial.print(BUTTON_NAMES[i]); Serial.println(" released");
      }
    }
    last = state;
  }

  delay(50);  // debounce delay
}
