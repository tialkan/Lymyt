// Arduino Nano ESP32; GxEPD2, Adafruit GFX, ArduinoJson 7.
// Select Tools > Pin Numbering > By Arduino pin (default).
#include <WiFi.h>
#include <HTTPClient.h>
#include <WiFiClientSecure.h>
#include <ArduinoJson.h>
#include <SPI.h>
#include <time.h>
#include "config.h"
#include <Preferences.h>
#include <U8g2_for_Adafruit_GFX.h>
#include "Words.h"
#include "Learning.h"
#ifndef LYMYT_OLED
#define LYMYT_OLED false
#endif
#if LYMYT_OLED
#include <Wire.h>
#include <Adafruit_SSD1306.h>
#else
#include <GxEPD2_BW.h>
#endif
#ifndef LYMYT_USB_SERIAL
#define LYMYT_USB_SERIAL false
#endif
#if LYMYT_USE_ADXL345
#include <Wire.h>
#include <Adafruit_ADXL345_U.h>
Adafruit_ADXL345_Unified accelerometer(345);
#endif

#if LYMYT_OLED
using EyeDisplay = Adafruit_SSD1306;
TwoWire rightBus(1);
EyeDisplay leftEye(128, 64, &Wire, -1);
EyeDisplay rightEye(128, 64, &rightBus, -1);
#else
using Panel = LYMYT_PANEL_CLASS;
using EyeDisplay = GxEPD2_BW<Panel, Panel::HEIGHT>;
EyeDisplay leftEye(Panel(D10, D9, D8, D7));
EyeDisplay rightEye(Panel(D6, D5, D4, D3));
#endif
U8G2_FOR_ADAFRUIT_GFX utf8;
Learning learning;
Preferences progress;
bool progressReady = false, displaysReady = true;

struct LimitWindow {
  bool present = false;
  float used = -1;
  uint32_t resetAt = 0;
};
struct Provider {
  LimitWindow shortWindow;
  LimitWindow weekWindow;
  uint32_t observedAt = 0;
  bool fresh = false;
};
Provider providers[2];
bool linked = false, weekly = false;
uint32_t epochBase = 0, epochMillis = 0;
uint32_t lastPoll = 0, lastDraw = 0, lastConnect = 0;
uint8_t refreshCount = 0;
bool firstFrame = true;
uint32_t sparkleUntil = 0;
uint32_t pressStarted = 0;
bool previousPress = false, pressHandled = false;
bool accelerometerReady = false, motion = false;
bool ntpStarted = false;
float accelX = 0, accelY = 0, accelZ = 0;
uint32_t lastSensorRead = 0, lastPresence = 0, lastShake = 0;
uint32_t interactionUntil = 0;
int tiltGaze = 0;
String serialFrame;
bool droppingSerialFrame = false;
uint32_t lastUsbHello = 0;

bool applyStatus(JsonDocument& document);

void readUsb() {
  if (!LYMYT_USB_SERIAL) return;
  // Bounded, non-blocking newline frames. Debug output is only host-bound.
  while (Serial.available()) {
    char ch = Serial.read();
    if (ch == '\n') {
      if (!droppingSerialFrame && serialFrame.length()) {
        JsonDocument document;
        if (!deserializeJson(document, serialFrame) && applyStatus(document)) {
          Serial.print("{\"lymyt\":\"ack\",\"generated_at\":");
          Serial.print(epochBase);
          Serial.print(",\"view\":\"");
          Serial.print(learning.words ? "words" : (weekly ? "week" : "short"));
          Serial.println("\"}");
        }
      }
      serialFrame = ""; droppingSerialFrame = false;
    } else if (ch != '\r' && !droppingSerialFrame) {
      if (serialFrame.length() >= 8192) {
        serialFrame = ""; droppingSerialFrame = true;
      } else serialFrame += ch;
    }
  }
  if (millis() - lastUsbHello >= 5000 && !linked) {
    Serial.println("{\"lymyt\":\"ready\",\"transport\":\"usb\"}");
    lastUsbHello = millis();
  }
  if (linked && millis() - lastPoll > 45000) linked = false;
}

bool beginHttp(HTTPClient& http, WiFiClient& plain, WiFiClientSecure& secure, const String& url) {
  if (url.startsWith("https://")) {
    if (!strlen(LYMYT_ROOT_CA)) return false;
    // TLS certificate validity needs the ESP32 system clock, not our display clock.
    if (time(nullptr) < 1700000000) return false;
    secure.setCACert(LYMYT_ROOT_CA);
    return http.begin(secure, url);
  }
  return url.startsWith("http://") && http.begin(plain, url);
}

void sendTelemetry() {
  if (WiFi.status() != WL_CONNECTED) return;
  String endpoint = LYMYT_BRIDGE_URL;
  if (!endpoint.endsWith("/v1/status")) return;
  endpoint.replace("/v1/status", "/v1/device");
  WiFiClient plain; WiFiClientSecure secure; HTTPClient http;
  http.setConnectTimeout(3000); http.setTimeout(3000);
  if (!beginHttp(http, plain, secure, endpoint)) return;
  JsonDocument data;
  data["view"] = learning.words ? "words" : (weekly ? "week" : "short");
  if (LYMYT_MOTION_PIN >= 0) data["motion"] = motion;
  if (accelerometerReady) {
    data["acceleration"]["x"] = accelX;
    data["acceleration"]["y"] = accelY;
    data["acceleration"]["z"] = accelZ;
  }
  String body; serializeJson(data, body);
  http.addHeader("Authorization", String("Bearer ") + LYMYT_DEVICE_TOKEN);
  http.addHeader("Content-Type", "application/json");
  http.POST(body); http.end();
}

void readSensors() {
  if (millis() - lastSensorRead < 100) return;
  lastSensorRead = millis();
  if (LYMYT_MOTION_PIN >= 0) {
    bool incoming = digitalRead(LYMYT_MOTION_PIN) == HIGH;
    if (incoming) lastPresence = millis();
    if (incoming && !motion) interactionUntil = millis() + 3000;
    motion = incoming;
  }
#if LYMYT_USE_ADXL345
  if (accelerometerReady) {
    sensors_event_t event; accelerometer.getEvent(&event);
    accelX = event.acceleration.x; accelY = event.acceleration.y; accelZ = event.acceleration.z;
    tiltGaze = constrain((int)(accelX * 2), -12, 12);
    float magnitude = sqrtf(accelX * accelX + accelY * accelY + accelZ * accelZ);
    if (fabsf(magnitude - 9.81f) > 3.0f && millis() - lastShake > 5000) {
      interactionUntil = millis() + 5000; lastShake = millis(); lastPresence = millis();
    }
  }
#endif
}

uint32_t clockNow() {
  return epochBase ? epochBase + (uint32_t)(millis() - epochMillis) / 1000 : 0;
}

LimitWindow parseWindow(JsonObjectConst data) {
  LimitWindow result;
  if (data.isNull()) return result;
  result.present = true;
  if (data["used_percent"].is<float>() || data["used_percent"].is<int>()) {
    float used = data["used_percent"].as<float>();
    if (isfinite(used) && used >= 0 && used <= 100) result.used = used;
  }
  if (data["resets_at"].is<uint32_t>()) result.resetAt = data["resets_at"].as<uint32_t>();
  return result;
}

Provider parseProvider(JsonObjectConst data) {
  Provider result;
  result.observedAt = data["observed_at"] | 0U;
  result.fresh = String(data["status"] | "unknown") == "ok";
  for (JsonObjectConst item : data["windows"].as<JsonArrayConst>()) {
    String id = item["id"] | "";
    int minutes = item["window_minutes"] | 0;
    if (id == "five_hour" || (id == "primary" && minutes < 1440)) result.shortWindow = parseWindow(item);
    else if (id == "seven_day" || minutes >= 1440) result.weekWindow = parseWindow(item);
  }
  return result;
}

bool renewed(const Provider& before, const Provider& after) {
  const LimitWindow& previous = weekly ? before.weekWindow : before.shortWindow;
  const LimitWindow& current = weekly ? after.weekWindow : after.shortWindow;
  return after.fresh && previous.used >= 100 && current.used >= 0 && current.used < 100
      && current.resetAt > previous.resetAt;
}

bool applyStatus(JsonDocument& document) {
  if (!document["schema_version"].is<int>() || document["schema_version"].as<int>() != 1
      || !document["generated_at"].is<uint32_t>()
      || !document["providers"]["openai"].is<JsonObject>()
      || !document["providers"]["claude"].is<JsonObject>()) return false;
  Provider incoming[] = {
    parseProvider(document["providers"]["openai"].as<JsonObjectConst>()),
    parseProvider(document["providers"]["claude"].as<JsonObjectConst>())
  };
  if (renewed(providers[0], incoming[0]) || renewed(providers[1], incoming[1])) sparkleUntil = millis() + 12000;
  providers[0] = incoming[0]; providers[1] = incoming[1];
  epochBase = document["generated_at"].as<uint32_t>();
  epochMillis = millis(); lastPoll = millis(); linked = true;
  return true;
}

void pollBridge() {
  lastPoll = millis();
  if (WiFi.status() != WL_CONNECTED) { linked = false; return; }
  HTTPClient http;
  WiFiClient plain; WiFiClientSecure secure;
  http.setConnectTimeout(3000);
  http.setTimeout(3000);
  if (!beginHttp(http, plain, secure, LYMYT_BRIDGE_URL)) { linked = false; return; }
  http.addHeader("Authorization", String("Bearer ") + LYMYT_DEVICE_TOKEN);
  int code = http.GET();
  if (code == 200) {
    JsonDocument document;
    DeserializationError error = deserializeJson(document, http.getString());
    linked = !error && applyStatus(document);
  } else linked = false;
  http.end();
  sendTelemetry();
}

String remainingTime(uint32_t resetAt, uint32_t now) {
  if (!resetAt || !now) return "--";
  if (now >= resetAt) return "DOGRULA";
  uint32_t minutes = (resetAt - now + 59) / 60;
  if (minutes >= 1440) return String(minutes / 1440) + "g " + String((minutes % 1440) / 60) + "s";
  if (minutes >= 60) return String(minutes / 60) + "s " + String(minutes % 60) + "dk";
  return String(minutes) + "dk";
}

bool providerFresh(const Provider& provider, uint32_t now) {
  return linked && provider.fresh && provider.observedAt && now >= provider.observedAt
      && now - provider.observedAt <= 180;
}

void centered(EyeDisplay& display, const String& text, int y, uint8_t size) {
  display.setTextSize(size);
  int16_t x1, y1; uint16_t width, height;
  display.getTextBounds(text, 0, y, &x1, &y1, &width, &height);
  display.setCursor((display.width() - width) / 2, y);
  display.print(text);
}

void utf8Center(EyeDisplay& display, const String& text, int y) {
  int x = max(2, (display.width() - (int)utf8.getUTF8Width(text.c_str())) / 2);
  utf8.setCursor(x, y); utf8.print(text);
}

void wordLines(EyeDisplay& display, const char* value) {
  String line, input(value);
  int y = LYMYT_OLED ? 27 : 85;
  int maxWidth = display.width() - 12;
  // Word wrapping preserves UTF-8 code points and measures actual glyph widths.
  while (input.length()) {
    int space = input.indexOf(' ');
    String token = space < 0 ? input : input.substring(0, space);
    input = space < 0 ? "" : input.substring(space + 1);
    String next = line.length() ? line + " " + token : token;
    if (utf8.getUTF8Width(next.c_str()) > maxWidth && line.length()) {
      utf8Center(display, line, y); y += 17; line = token;
    } else line = next;
  }
  utf8Center(display, line, y);
}

void drawEye(EyeDisplay& display, const Provider& provider, const char* label, bool full, int gaze, bool isRight) {
  const LimitWindow& selected = weekly ? provider.weekWindow : provider.shortWindow;
  uint32_t now = clockNow();
  bool fresh = providerFresh(provider, now);
  int capacity = selected.used < 0 ? -1 : roundf(100 - selected.used);
#if !LYMYT_OLED
  if (full) display.setFullWindow();
  else display.setPartialWindow(0, 0, display.width(), display.height());
  display.firstPage();
#endif
  do {
    // Adafruit OLED uses black=0/white=1; e-paper uses the inverse.
    const uint16_t ink = LYMYT_OLED ? 1 : 0, paper = LYMYT_OLED ? 0 : 1;
    display.fillScreen(paper); display.setTextColor(ink);
    utf8.begin(display); utf8.setFont(u8g2_font_unifont_t_extended);
    utf8.setForegroundColor(ink); utf8.setBackgroundColor(paper); utf8.setFontMode(1);
    if (learning.words) {
      display.setTextSize(1); display.setCursor(5, 2);
      display.print(isRight ? "TR / C1" : "EN / C1");
      wordLines(display, isRight ? WORDS[learning.index].tr : WORDS[learning.index].en);
      display.setTextSize(1); display.setCursor(5, display.height() - 10);
      display.print(String(learning.index + 1) + "/" + String(WORD_COUNT));
    } else {
      centered(display, String(label) + (weekly ? " 7D" : ""), LYMYT_OLED ? 0 : 12, LYMYT_OLED ? 1 : 2);
      int cx = display.width()/2 + gaze + tiltGaze;
      int cy = LYMYT_OLED ? 23 : 89;
      bool napping = LYMYT_MOTION_PIN >= 0 && millis() - lastPresence >= 300000;
      if (!fresh || capacity < 0) display.fillCircle(cx, cy, LYMYT_OLED ? 4 : 12, ink);
      else if (capacity == 0 || napping) display.fillRoundRect(cx-(LYMYT_OLED?15:46),cy,LYMYT_OLED?30:92,LYMYT_OLED?3:8,2,ink);
      else {
        int w = LYMYT_OLED ? 17 : 64, h = LYMYT_OLED ? 18 : (capacity <= 20 ? 40 : 81);
        display.fillRoundRect(cx-w/2,cy-h/2,w,h,LYMYT_OLED?7:17,ink);
        display.fillCircle(cx-w/5,cy-h/4,LYMYT_OLED?2:7,paper);
      }
      centered(display, capacity < 0 ? "VERI YOK" : String(capacity) + "% KALDI", LYMYT_OLED ? 37 : 146, LYMYT_OLED ? 1 : 2);
      centered(display, remainingTime(selected.resetAt, now), LYMYT_OLED ? 49 : 169, LYMYT_OLED ? 1 : 2);
      if (!fresh && capacity >= 0) centered(display, "SON BILINEN", LYMYT_OLED ? 57 : 190, 1);
    }
#if LYMYT_OLED
    display.display();
  } while (false);
#else
  } while (display.nextPage());
  display.epd2.powerOff();
#endif
}

void updateLight() {
  if (LYMYT_LED_PIN < 0) return;
  bool celebrate = (int32_t)(sparkleUntil - millis()) > 0;
  bool responding = (int32_t)(interactionUntil - millis()) > 0;
  bool on = learning.pending ? (millis() / 250) % 2 : celebrate ? (millis() / 180) % 2 : responding ? (millis() / 400) % 2 : linked;
  digitalWrite(LYMYT_LED_PIN, on ? HIGH : LOW);
}

void updateButton() {
  if (LYMYT_BUTTON_PIN < 0) return;
  bool pressed = digitalRead(LYMYT_BUTTON_PIN) == LOW;
  if (pressed && !previousPress) { pressStarted = millis(); pressHandled = false; }
  if (pressed && !pressHandled && millis() - pressStarted >= 40) {
    pressHandled = true;
    uint32_t previousLearned = learning.learned;
    if (learning.press(WORD_COUNT)) {
      interactionUntil = millis() + 1500;
      if (progressReady && learning.learned != previousLearned) {
        progress.putUInt("learned", learning.learned);
        progress.putUChar("index", learning.index);
      }
      Serial.println(learning.words ? "Word view queued" : "Limit view queued");
    }
  }
  previousPress = pressed;
}

void setup() {
  Serial.begin(115200);
  serialFrame.reserve(2048);
  pinMode(D10, OUTPUT); digitalWrite(D10, HIGH);
  pinMode(D6, OUTPUT); digitalWrite(D6, HIGH);
  if (LYMYT_LED_PIN >= 0) pinMode(LYMYT_LED_PIN, OUTPUT);
  if (LYMYT_BUTTON_PIN >= 0) pinMode(LYMYT_BUTTON_PIN, INPUT_PULLUP);
  if (LYMYT_MOTION_PIN >= 0) pinMode(LYMYT_MOTION_PIN, INPUT);
#if LYMYT_USE_ADXL345
  Wire.begin();
  accelerometerReady = accelerometer.begin(LYMYT_ADXL_ADDRESS);
  if (accelerometerReady) accelerometer.setRange(ADXL345_RANGE_4_G);
#endif
  lastPresence = millis();
  progressReady = progress.begin("lymyt-c1", false);
  if (progressReady) {
    learning.index = progress.getUChar("index", 0) % WORD_COUNT;
    learning.learned = progress.getUInt("learned", 0);
  }
#if LYMYT_OLED
  // Separate hardware buses allow two modules with the same 0x3C address.
  Wire.begin(A4, A5);
  rightBus.begin(A2, A3);
  displaysReady = leftEye.begin(SSD1306_SWITCHCAPVCC, 0x3C, true, false);
  if (LYMYT_RIGHT_EYE_ENABLED) displaysReady = rightEye.begin(SSD1306_SWITCHCAPVCC, 0x3C, true, false) && displaysReady;
#else
  SPI.begin();
  leftEye.init(115200, true, 5, false);
  if (LYMYT_RIGHT_EYE_ENABLED) rightEye.init(115200, true, 5, false);
#endif
  if (!displaysReady) Serial.println("Display initialization failed; check power/I2C address.");
  if (LYMYT_USB_SERIAL) {
    Serial.println("{\"lymyt\":\"ready\",\"transport\":\"usb\"}");
  } else {
    WiFi.mode(WIFI_STA);
    WiFi.begin(LYMYT_WIFI_SSID, LYMYT_WIFI_PASSWORD);
  }
  lastConnect = millis();
}

void loop() {
  readSensors(); updateButton(); readUsb(); updateLight();
  if (!LYMYT_USB_SERIAL && !ntpStarted && WiFi.status() == WL_CONNECTED && String(LYMYT_BRIDGE_URL).startsWith("https://")) {
    configTime(0, 0, "time.cloudflare.com", "pool.ntp.org");
    ntpStarted = true;
  }
  if (!LYMYT_USB_SERIAL && WiFi.status() != WL_CONNECTED && millis() - lastConnect >= 30000) {
    WiFi.reconnect(); lastConnect = millis();
  }
  if (!LYMYT_USB_SERIAL && (!lastPoll || millis() - lastPoll >= 15000)) pollBridge();
  const uint32_t interval = LYMYT_OLED ? (learning.pending ? 50 : 1000) : (LYMYT_PARTIAL_REFRESH ? 60000 : 180000);
  bool readyForFirstFrame = !LYMYT_USB_SERIAL || linked || millis() >= 30000;
  if (displaysReady && ((firstFrame && readyForFirstFrame) || (!firstFrame && millis() - lastDraw >= interval))) {
    bool full = firstFrame || !LYMYT_PARTIAL_REFRESH || refreshCount >= 5;
    drawEye(leftEye, providers[0], "CODEX", full, 5, false);
    if (LYMYT_RIGHT_EYE_ENABLED) drawEye(rightEye, providers[1], "CLAUDE", full, -5, true);
    refreshCount = full ? 0 : refreshCount + 1;
    learning.displayed();
    firstFrame = false; lastDraw = millis();
  }
  delay(5);
}
