#pragma once

// Classic ESP32-WROOM: copy this file to config.h. Never commit Wi-Fi passwords or the device token.
// USB mode: bridge/lymyt.py serve --serial-port /dev/cu.usbserial...
// Uses the USB data cable; Wi-Fi credentials and HTTP token are unused.
#define LYMYT_USB_SERIAL true

// false: Waveshare 1.54 B/W. true: two 128x64 SSD1306 I2C modules.
// OLED left SDA=21/SCL=22; right SDA=16/SCL=17; both VCC=3V3.
#define LYMYT_OLED false
#define LYMYT_WIFI_SSID "your-2.4GHz-WiFi"
#define LYMYT_WIFI_PASSWORD "your-WiFi-password"
#define LYMYT_BRIDGE_URL "http://192.168.1.10:8787/v1/status"
#define LYMYT_DEVICE_TOKEN "contents-of-.lymyt/device-token"

// Provisional driver for the linked Waveshare 1.54-inch B/W V2 (SSD1681).
// Confirm the panel/V2 marking with a single-screen manufacturer example first.
// Rev2.1 describes the carrier board, not necessarily the panel controller.
#define LYMYT_PANEL_CLASS GxEPD2_154_D67

// Set false for the first bench test with only the left screen attached.
#define LYMYT_RIGHT_EYE_ENABLED true

// Leave false for the first hardware check. Enable only after partial refresh
// is verified on the actual panel. Full cleanup occurs after 5 partial updates.
#define LYMYT_PARTIAL_REFRESH false

// Optional simple LED: GPIO13 -> 330 ohm resistor -> LED anode; cathode -> GND.
// LED-free design: keep -1. GPIO18 is the SPI clock; do not use it for an LED.
#define LYMYT_LED_PIN -1

// Optional momentary button: GPIO4 -> button -> GND. No external pull-up required.
#define LYMYT_BUTTON_PIN -1

// ADXL345 via I2C: SDA=21, SCL=22, VCC=3V3, GND=GND.
// Enable after wiring; requires Adafruit ADXL345 + Adafruit Unified Sensor.
#define LYMYT_USE_ADXL345 false
#define LYMYT_ADXL_ADDRESS 0x53

// Motion sensor output -> GPIO19. Keep -1 until sensor model/output is confirmed.
#define LYMYT_MOTION_PIN -1

// For future HTTPS VPS access, provide the trusted root CA certificate.
// Do not disable certificate validation. LAN HTTP does not need a certificate.
static const char LYMYT_ROOT_CA[] = "";
