#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define OLED_WIDTH 128
#define OLED_HEIGHT 64
Adafruit_SSD1306 display(OLED_WIDTH, OLED_HEIGHT, &Wire, -1);

// HC-SR04 sensör pinleri
#define TRIG_ARKA 2
#define ECHO_ARKA 3
#define TRIG_ON 4
#define ECHO_ON 5

long mesafe_arka = 0;
long mesafe_on = 0;

String durum = "TARTIM YOK";
String mesaj = "Bekleniyor...";
String plaka = "---";
String kg = "---";

bool tartimda = false;
bool tartimBittiGosterildi = false;
unsigned long tartimBittiZaman = 0;

void setup() {
  Serial.begin(9600);
  pinMode(TRIG_ARKA, OUTPUT);
  pinMode(ECHO_ARKA, INPUT);
  pinMode(TRIG_ON, OUTPUT);
  pinMode(ECHO_ON, INPUT);

  display.begin(SSD1306_SWITCHCAPVCC, 0x3C);
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.display();
}

long olc(int trigPin, int echoPin) {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(5);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  long sure = pulseIn(echoPin, HIGH, 30000); // 30ms timeout
  if (sure == 0) return 999;
  return sure * 0.034 / 2;
}

void ekranaYaz() {
  display.clearDisplay();
  display.setCursor(0, 0);

  if (durum == "TARTIM BİTTİ") {
    display.println("Durum: TARTIM BİTTİ");
    display.println("Plaka: " + plaka);
    display.println("Agirlik: " + kg + " kg");
  } else {
    display.println("Durum: " + durum);
    display.println("Mesaj: " + mesaj);
  }

  display.display();
}

void loop() {
  // Önce gelen seri verisini oku
  if (Serial.available()) {
    String veri = Serial.readStringUntil('\n');
    veri.trim();

    if (veri.startsWith("DATA:")) {
      int ayirac = veri.indexOf('|');
      if (ayirac > 5) {
        plaka = veri.substring(5, ayirac);
        kg = veri.substring(ayirac + 1);
        durum = "TARTIM BİTTİ";
        tartimBittiZaman = millis();
        tartimBittiGosterildi = true;
        tartimda = false;
      }
    } else if (veri == "TARTIM_BITTI") {
      // Python tarafından tekrar yollandıysa
      durum = "TARTIM YOK";
      mesaj = "Bekleniyor...";
      plaka = "---";
      kg = "---";
      tartimda = false;
      tartimBittiGosterildi = false;
    }
  }

  // TARTIM BİTTİ ekranı 5 saniye gösterildiyse sıfırla
  if (durum == "TARTIM BİTTİ" && tartimBittiGosterildi && millis() - tartimBittiZaman > 5000) {
    durum = "TARTIM YOK";
    mesaj = "Bekleniyor...";
    plaka = "---";
    kg = "---";
    tartimBittiGosterildi = false;
  }

  // Tartımda değilsek mesafeye bak
  if (!tartimda && durum != "TARTIM BİTTİ") {
    mesafe_arka = olc(TRIG_ARKA, ECHO_ARKA);
    mesafe_on = olc(TRIG_ON, ECHO_ON);

    if (mesafe_arka < 15 && mesafe_on > 20) {
      mesaj = "Ona ilerle";
      durum = "TARTIM YOK";
    } else if (mesafe_on < 15 && mesafe_arka > 20) {
      mesaj = "Geri git";
      durum = "TARTIM YOK";
    } else if (mesafe_on < 15 && mesafe_arka < 15) {
      mesaj = "Konum iyi";
      durum = "TARTIMDA";
      tartimda = true;
      Serial.println("TARTIM");
    } else {
      mesaj = "Bekleniyor...";
      durum = "TARTIM YOK";
    }
  }

  ekranaYaz();
  delay(300);
}
