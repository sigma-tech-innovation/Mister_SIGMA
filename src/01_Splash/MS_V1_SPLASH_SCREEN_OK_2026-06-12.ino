#include <TFT_eSPI.h>
#include <SPI.h>
#include <XPT2046_Touchscreen.h>

TFT_eSPI tft = TFT_eSPI();

// Pins tactiles CYD ESP32-2432S028R
#define TOUCH_CS   33
#define TOUCH_IRQ  36
#define TOUCH_MOSI 32
#define TOUCH_MISO 39
#define TOUCH_CLK  25

SPIClass touchSPI = SPIClass(VSPI);
XPT2046_Touchscreen ts(TOUCH_CS, TOUCH_IRQ);

#define COLOR_BG      TFT_BLACK
#define COLOR_BORDER  TFT_WHITE
#define COLOR_LOGO    TFT_GREEN
#define COLOR_TITLE   TFT_WHITE
#define COLOR_MENU    TFT_GREEN
#define COLOR_INFO    TFT_WHITE
#define COLOR_COMPANY TFT_YELLOW
#define COLOR_SYSTEM  TFT_CYAN
#define COLOR_LOAD    TFT_GREEN
#define COLOR_TOUCH   TFT_DARKGREEN

const int SCREEN_W = 320;
const int SCREEN_H = 240;

const int BTN_X = 50;
const int BTN_W = 220;
const int BTN_H = 45;
const int BTN1_Y = 88;
const int BTN2_Y = 148;

void drawSigmaLogo(int cx, int cy, uint16_t color) {
  int s = 34;
  tft.drawLine(cx - s / 2, cy - s / 2, cx + s / 2, cy - s / 2, color);
  tft.drawLine(cx - s / 2, cy - s / 2, cx + 4, cy, color);
  tft.drawLine(cx + 4, cy, cx - s / 2, cy + s / 2, color);
  tft.drawLine(cx - s / 2, cy + s / 2, cx + s / 2, cy + s / 2, color);
  tft.drawLine(cx - s / 2, cy - s / 2 + 1, cx + s / 2, cy - s / 2 + 1, color);
  tft.drawLine(cx - s / 2, cy + s / 2 - 1, cx + s / 2, cy + s / 2 - 1, color);
}

void drawCenteredText(const char* text, int y, int size, uint16_t color) {
  tft.setTextDatum(MC_DATUM);
  tft.setTextSize(size);
  tft.setTextColor(color, COLOR_BG);
  tft.drawString(text, SCREEN_W / 2, y);
}

void drawDashedBorder() {
  int x = 22, y = 18, w = 276, h = 204;
  int dash = 10, gap = 6;

  for (int i = x; i < x + w; i += dash + gap) {
    tft.drawLine(i, y, min(i + dash, x + w), y, COLOR_BORDER);
    tft.drawLine(i, y + h, min(i + dash, x + w), y + h, COLOR_BORDER);
  }

  for (int i = y; i < y + h; i += dash + gap) {
    tft.drawLine(x, i, x, min(i + dash, y + h), COLOR_BORDER);
    tft.drawLine(x + w, i, x + w, min(i + dash, y + h), COLOR_BORDER);
  }
}

void animateLoadingBar() {
  int blocks = 8, size = 12, gap = 6;
  int startX = 91, y = 205;
  unsigned long startTime = millis();

  while (millis() - startTime < 3000) {
    for (int active = 0; active < blocks; active++) {
      for (int i = 0; i < blocks; i++) {
        int x = startX + i * (size + gap);

        if (i == active) {
          tft.fillRect(x, y, size, size, COLOR_LOAD);
        } else {
          tft.fillRect(x, y, size, size, COLOR_BG);
          tft.drawRect(x, y, size, size, COLOR_LOAD);
        }
      }
      delay(120);
    }
  }
}

void showSplashScreen() {
  tft.fillScreen(COLOR_BG);
  drawDashedBorder();

  drawSigmaLogo(160, 55, COLOR_LOGO);

  drawCenteredText("MISTER SIGMA", 105, 2, COLOR_TITLE);
  drawCenteredText("Sigma Tech Innovation", 145, 2, COLOR_COMPANY);
  drawCenteredText("Industrial Training System", 172, 1, COLOR_SYSTEM);
  drawCenteredText("CHARGEMENT...", 192, 2, COLOR_LOAD);

  animateLoadingBar();
  delay(400);
}

void drawMenuButton(const char* text, int y, bool pressed = false) {
  uint16_t fillColor = pressed ? COLOR_TOUCH : COLOR_BG;

  tft.fillRoundRect(BTN_X, y, BTN_W, BTN_H, 8, fillColor);
  tft.drawRoundRect(BTN_X, y, BTN_W, BTN_H, 8, COLOR_MENU);
  tft.drawRoundRect(BTN_X + 1, y + 1, BTN_W - 2, BTN_H - 2, 8, COLOR_MENU);

  tft.setTextDatum(MC_DATUM);
  tft.setTextSize(2);
  tft.setTextColor(COLOR_MENU, fillColor);
  tft.drawString(text, BTN_X + BTN_W / 2, y + BTN_H / 2);
}

void showMainMenuPage1() {
  tft.fillScreen(COLOR_BG);

  drawSigmaLogo(160, 28, COLOR_LOGO);
  drawCenteredText("MISTER SIGMA", 58, 2, COLOR_TITLE);

  drawMenuButton("AUTOMATISME", BTN1_Y);
  drawMenuButton("ELECTRICITE", BTN2_Y);

  drawCenteredText("<   Page 1/10   >", 220, 1, COLOR_INFO);
}

bool isInsideButton(int x, int y, int btnY) {
  return (x >= BTN_X && x <= BTN_X + BTN_W && y >= btnY && y <= btnY + BTN_H);
}

void handleTouch() {
  if (ts.touched()) {
    TS_Point p = ts.getPoint();

    int x = map(p.x, 200, 3700, 0, 320);
    int y = map(p.y, 240, 3800, 0, 240);

    x = constrain(x, 0, 319);
    y = constrain(y, 0, 239);

    Serial.print("X = ");
    Serial.print(x);
    Serial.print(" | Y = ");
    Serial.println(y);

    if (isInsideButton(x, y, BTN1_Y)) {
      drawMenuButton("AUTOMATISME", BTN1_Y, true);
      delay(200);
      drawMenuButton("AUTOMATISME", BTN1_Y, false);
    }

    if (isInsideButton(x, y, BTN2_Y)) {
      drawMenuButton("ELECTRICITE", BTN2_Y, true);
      delay(200);
      drawMenuButton("ELECTRICITE", BTN2_Y, false);
    }

    delay(150);
  }
}

void setup() {
  Serial.begin(115200);

  tft.init();
  tft.setRotation(1);
  tft.fillScreen(COLOR_BG);

  touchSPI.begin(TOUCH_CLK, TOUCH_MISO, TOUCH_MOSI, TOUCH_CS);
  ts.begin(touchSPI);
  ts.setRotation(1);

  showSplashScreen();
  showMainMenuPage1();
}

void loop() {
  handleTouch();
}