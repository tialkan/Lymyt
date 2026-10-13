// Standalone bench test for classic ESP32-WROOM. Use ESP32 Dev Module.
// No Wi-Fi, quota bridge, sensors or automatic refresh. Send l / r / s at 115200.
// Provisional B/W V2 SSD1681 driver; carrier rev2.1 alone does not identify it.
#include <Arduino.h>
#include <sdkconfig.h>
#if !defined(CONFIG_IDF_TARGET_ESP32)
#error "Select ESP32 Dev Module for a classic ESP32-WROOM board."
#endif
#include <SPI.h>
#include <GxEPD2_BW.h>
#include <driver/gpio.h>

using Panel = GxEPD2_154_D67;
using Display = GxEPD2_BW<Panel, Panel::HEIGHT>;
Display left(Panel(27, 26, 25, 34));
Display right(Panel(33, 32, 14, 35));
volatile uint32_t busyEdges[2] = {0, 0};
volatile uint32_t busyHighEdges[2] = {0, 0};
gpio_num_t busyGpio[2];
bool tested[2] = {false, false};
uint32_t testedAt[2] = {0, 0};

void IRAM_ATTR leftBusyChanged() {
  ++busyEdges[0];
  if (gpio_get_level(busyGpio[0])) ++busyHighEdges[0];
}
void IRAM_ATTR rightBusyChanged() {
  ++busyEdges[1];
  if (gpio_get_level(busyGpio[1])) ++busyHighEdges[1];
}

void reportPins() {
  Serial.printf("BUSY left(34)=%d right(35)=%d\n", digitalRead(34), digitalRead(35));
  Serial.printf("GPIO SCK(18)=%d MOSI(23)=%d; left CS/DC/RST/BUSY=%d/%d/%d/%d; right=%d/%d/%d/%d\n",
    18, 23,
    27, 26,
    25, 34,
    33, 32,
    14, 35);
}

void checkPanel(uint8_t index) {
  if (tested[index] && millis() - testedAt[index] < 180000) {
    Serial.println("Wait 3 minutes before retesting this panel.");
    return;
  }
  // Deselect the other screen for the entire test.
  digitalWrite(index == 0 ? 33 : 27, HIGH);
  Display& display = index == 0 ? left : right;
  busyEdges[index] = 0;
  busyHighEdges[index] = 0;
  Serial.printf("BEGIN %s: 1 MHz SPI, 5 ms reset, single full frame\n", index == 0 ? "LEFT" : "RIGHT");
  uint32_t started = millis();
  // 5 ms reset follows Waveshare's V2 example. BUSY remains an input.
  display.init(115200, true, 5, false);
  display.setRotation(0);
  display.setFullWindow();
  display.firstPage();
  do {
    display.fillScreen(GxEPD_WHITE);
    display.fillRect(0, 0, 200, 65, GxEPD_BLACK);
    display.setTextColor(GxEPD_WHITE);
    display.setTextSize(3);
    display.setCursor(17, 20);
    display.print("LYMYT");
    display.setTextColor(GxEPD_BLACK);
    display.setTextSize(2);
    display.setCursor(40, 85);
    display.print(index == 0 ? "LEFT" : "RIGHT");
    display.fillCircle(60, 135, 22, GxEPD_BLACK);
    display.fillCircle(140, 135, 22, GxEPD_BLACK);
    display.drawRect(0, 0, 200, 200, GxEPD_BLACK);
  } while (display.nextPage());
  uint32_t refreshMs = millis() - started;
  // Do not cut panel power immediately when an absent BUSY wire reads LOW.
  delay(5000);
  display.epd2.powerOff();
  Serial.printf("RESULT %s refresh_ms=%lu busy_edges=%lu high_edges=%lu busy_now=%d\n",
    index == 0 ? "LEFT" : "RIGHT", (unsigned long)refreshMs,
    (unsigned long)busyEdges[index], (unsigned long)busyHighEdges[index],
    digitalRead(index == 0 ? 34 : 35));
  Serial.println("Software completion is not proof of a visible image.");
  tested[index] = true;
  testedAt[index] = millis();
}

void setup() {
  Serial.begin(115200);
  pinMode(27, OUTPUT); digitalWrite(27, HIGH);
  pinMode(33, OUTPUT); digitalWrite(33, HIGH);
  pinMode(34, INPUT); pinMode(35, INPUT);
  busyGpio[0] = (gpio_num_t)34;
  busyGpio[1] = (gpio_num_t)35;
  attachInterrupt(34, leftBusyChanged, CHANGE);
  attachInterrupt(35, rightBusyChanged, CHANGE);
  // Explicit classic ESP32 GPIO numbers; MOSI=23 and SCK=18.
  SPI.begin(18, -1, 23, -1);
  left.epd2.selectSPI(SPI, SPISettings(1000000, MSBFIRST, SPI_MODE0));
  right.epd2.selectSPI(SPI, SPISettings(1000000, MSBFIRST, SPI_MODE0));
  Serial.println("PanelCheckWroom ready: s=pins, l=left, r=right. LED-free.");
}

void loop() {
  if (Serial.available()) {
    char command = Serial.read();
    if (command == 's') { Serial.println("PanelCheck ready: l=left r=right s=pins"); reportPins(); }
    if (command == 'l') checkPanel(0);
    if (command == 'r') checkPanel(1);
  }
  delay(5);
}
