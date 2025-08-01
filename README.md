# ⚖️ Akıllı Kantar Sistemi

Bu sistem, **Arduino** ve **Python** kullanarak araçların konumuna göre otomatik tartım yapar. Araç doğru konumdaysa, sistem fotoğraf çeker, **Google Vision API** ile plaka tanır, ardından ağırlığı belirleyerek bilgileri **OLED ekrana** yansıtır ve **Excel dosyasına** kaydeder.

---

## 🧰 Gerekli Malzemeler

| Malzeme                  | Miktar | Açıklama                                                |
|--------------------------|--------|----------------------------------------------------------|
| Arduino UNO/Nano         | 1      | Sistem kontrolcüsü                                       |
| HC-SR04 Ultrasonik Sensör| 2      | Konum tespiti için (ön ve arka sensör)                  |
| OLED Ekran (SSD1306)     | 1      | Tartım bilgilerini ekranda göstermek için               |
| Kamera (USB/Webcam)      | 1      | Plaka fotoğrafı çekmek için                             |
| USB Kablosu              | 1      | Arduino-PC bağlantısı için                              |
| Python kurulu PC         | 1      | Plaka tanıma ve veri kaydı işlemleri için               |
| Jumper Kablo             | 10+    | Bağlantılar için                                        |
| Breadboard (opsiyonel)   | 1      | Daha düzenli devre kurulumu için                        |

---

## 🔌 Bağlantı Şeması

### HC-SR04 (Arka Sensör)
| Pin       | Arduino |
|-----------|---------|
| VCC       | 5V      |
| GND       | GND     |
| TRIG      | D2      |
| ECHO      | D3      |

### HC-SR04 (Ön Sensör)
| Pin       | Arduino |
|-----------|---------|
| VCC       | 5V      |
| GND       | GND     |
| TRIG      | D4      |
| ECHO      | D5      |

### OLED Ekran (SSD1306 - I2C)
| OLED Pin | Arduino Pin |
|----------|-------------|
| VCC      | 5V          |
| GND      | GND         |
| SDA      | A4          |
| SCL      | A5          |

> **Not:** I2C pinleri Arduino modeline göre farklılık gösterebilir.

---

## 🧠 Sistem Akışı

1. Araç iki sensör arasında doğru konuma gelince Arduino, PC'ye `TARTIM` sinyali gönderir.
2. Python scripti kameradan ya da dosya yolundaki fotoğraftan plaka fotoğrafı alır.
3. Fotoğraf OCR ile analiz edilir ve plaka tanımlanır.
4. Ağırlık bilgisi simüle edilerek (veya load cell entegresiyle gerçek veriyle) alınır.
5. OLED ekranda "TARTIM BİTTİ", plaka ve ağırlık gösterilir.
6. Tüm veriler `tartim_kayitlari.xlsx` dosyasına aşağıdaki formatta kaydedilir:

| Tarih | Saat | Plaka | Ağırlık (kg) | Lokasyon | Fotoğraf Yolu |
|-------|------|--------|--------------|----------|----------------|

---

## 💻 Gerekli Yazılım ve Kurulum

### Arduino IDE
- Kütüphaneler:
  - `Adafruit_GFX`
  - `Adafruit_SSD1306`

### Python 3.10+
- Gerekli modüller:
```bash
pip install opencv-python pandas google-cloud-vision openpyxl

---

## 📷 Örnek Terminal Çıktısı
📥 Arduino'dan gelen: TARTIM
✅ Konum doğru! Tartıma geçiliyor...
🚚 Plaka: 35ABC123, Ağırlık: 26300 kg
📤 Veri gönderildi: DATA:35ABC123|26300
✅ Excel'e kaydedildi: tartim_kayitlari.xlsx
