#pragma once

// Copy to config.h. Never commit Wi-Fi passwords or the device token.
// USB mode: bridge/lymyt.py serve --serial-port /dev/cu.usbmodem...
// Uses the USB data cable; Wi-Fi credentials and HTTP token are unused.
#define LYMYT_USB_SERIAL false
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

// Optional simple LED: A0 -> 330 ohm resistor -> LED anode; cathode -> GND.
// Keep -1 until wired. D13 / LED_BUILTIN is already used as the SPI clock.
#define LYMYT_LED_PIN -1

// Optional momentary button: D2 -> button -> GND. No external pull-up required.
#define LYMYT_BUTTON_PIN -1

// ADXL345 via I2C: SDA=A4, SCL=A5, VCC=3V3, GND=GND.
// Enable after wiring; requires Adafruit ADXL345 + Adafruit Unified Sensor.
#define LYMYT_USE_ADXL345 false
#define LYMYT_ADXL_ADDRESS 0x53

// Motion sensor output -> A1. Keep -1 until sensor model/output is confirmed.
#define LYMYT_MOTION_PIN -1

// For future HTTPS VPS access, provide the trusted root CA certificate.
// Do not disable certificate validation. LAN HTTP does not need a certificate.
static const char LYMYT_ROOT_CA[] = "";
