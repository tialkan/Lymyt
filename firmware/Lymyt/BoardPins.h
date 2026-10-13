#pragma once
#include <Arduino.h>
#include <sdkconfig.h>

// Numbers below are GPIO numbers on classic ESP32-WROOM, Arduino labels on Nano.
namespace BoardPins {
#if defined(ARDUINO_NANO_ESP32)
constexpr int sck = D13, mosi = D11;
constexpr int leftCs = D10, leftDc = D9, leftRst = D8, leftBusy = D7;
constexpr int rightCs = D6, rightDc = D5, rightRst = D4, rightBusy = D3;
constexpr int leftSda = A4, leftScl = A5, rightSda = A2, rightScl = A3;
#elif defined(CONFIG_IDF_TARGET_ESP32)
constexpr int sck = 18, mosi = 23;
constexpr int leftCs = 27, leftDc = 26, leftRst = 25, leftBusy = 34;
constexpr int rightCs = 33, rightDc = 32, rightRst = 14, rightBusy = 35;
constexpr int leftSda = 21, leftScl = 22, rightSda = 16, rightScl = 17;
#else
#error "Supported boards: Arduino Nano ESP32 or classic ESP32-WROOM. Check your board selection."
#endif
}
