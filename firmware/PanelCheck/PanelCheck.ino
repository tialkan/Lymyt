// Standalone bench test. Nano ESP32, Pin Numbering: By Arduino pin.
// No Wi-Fi, quota bridge, sensors or automatic refresh. Send l / r / s at 115200.
// Provisional B/W V2 SSD1681 driver; carrier rev2.1 alone does not identify it.
#include <Arduino.h>
#include <SPI.h>
#include <GxEPD2_BW.h>
#include <driver/gpio.h>

using Panel = GxEPD2_154_D67;
using Display = GxEPD2_BW<Panel, Panel::HEIGHT>;
Display left(Panel(D10, D9, D8, D7));
Display right(Panel(D6, D5, D4, D3));
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
  Serial.printf("BUSY left(D7)=%d right(D3)=%d\n", digitalRead(D7), digitalRead(D3));
  Serial.printf("GPIO SCK(D13)=%d MOSI(D11)=%d; left CS/DC/RST/BUSY=%d/%d/%d/%d; right=%d/%d/%d/%d\n",
    digitalPinToGPIONumber(D13), digitalPinToGPIONumber(D11),
    digitalPinToGPIONumber(D10), digitalPinToGPIONumber(D9),
    digitalPinToGPIONumber(D8), digitalPinToGPIONumber(D7),
    digitalPinToGPIONumber(D6), digitalPinToGPIONumber(D5),
    digitalPinToGPIONumber(D4), digitalPinToGPIONumber(D3));
}

void checkPanel(uint8_t index) {
  if (tested[index] && millis() - testedAt[index] < 180000) {
    Serial.println("Wait 3 minutes before retesting this panel.");
    return;
  }
  // Deselect the other screen for the entire test.
  digitalWrite(index == 0 ? D6 : D10, HIGH);
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
    digitalRead(index == 0 ? D7 : D3));
  Serial.println("Software completion is not proof of a visible image.");
  tested[index] = true;
  testedAt[index] = millis();
}

void setup() {
  Serial.begin(115200);
  pinMode(D10, OUTPUT); digitalWrite(D10, HIGH);
  pinMode(D6, OUTPUT); digitalWrite(D6, HIGH);
  pinMode(D7, INPUT); pinMode(D3, INPUT);
  pinMode(A0, OUTPUT); digitalWrite(A0, LOW);
  busyGpio[0] = (gpio_num_t)digitalPinToGPIONumber(D7);
  busyGpio[1] = (gpio_num_t)digitalPinToGPIONumber(D3);
  attachInterrupt(D7, leftBusyChanged, CHANGE);
  attachInterrupt(D3, rightBusyChanged, CHANGE);
  // Explicit Arduino pin labels; do not substitute physical GPIO numbers.
  SPI.begin(D13, -1, D11, -1);
  left.epd2.selectSPI(SPI, SPISettings(1000000, MSBFIRST, SPI_MODE0));
  right.epd2.selectSPI(SPI, SPISettings(1000000, MSBFIRST, SPI_MODE0));
}

void loop() {
  // Slow heartbeat on the existing A0 LED; never use D13 (SPI clock).
  digitalWrite(A0, millis() % 2000 < 150 ? HIGH : LOW);
  if (Serial.available()) {
    char command = Serial.read();
    if (command == 's') { Serial.println("PanelCheck ready: l=left r=right s=pins"); reportPins(); }
    if (command == 'l') checkPanel(0);
    if (command == 'r') checkPanel(1);
  }
  delay(5);
}
