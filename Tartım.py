import cv2
import time
import serial
import io
import os
import random
import re
from datetime import datetime
import pandas as pd
from google.cloud import vision
from google.oauth2 import service_account

# Google Vision API ayarları
credentials = service_account.Credentials.from_service_account_file("tartim.json")
client = vision.ImageAnnotatorClient(credentials=credentials)

# Arduino seri port bağlantısı (portu kendi sistemine göre ayarla)
arduino = serial.Serial('COM4', 9600, timeout=1)
time.sleep(2)  # Arduino reset için bekle

EXCEL_FILE = "tartim_kayitlari.xlsx"
LOCATION = "Izmir/Gaziemir ESBAS"

def turkce_to_ascii(text):
    replace_map = {
        "ç": "c", "ğ": "g", "ı": "i", "ö": "o", "ş": "s", "ü": "u",
        "Ç": "C", "Ğ": "G", "İ": "I", "Ö": "O", "Ş": "S", "Ü": "U"
    }
    for turkce, ascii_char in replace_map.items():
        text = text.replace(turkce, ascii_char)
    return text

def capture_plate_image():
    cap = cv2.VideoCapture(0)
    print("Kamera açık. 'b' tuşuna basarak görüntü al.")
    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        cv2.imshow("Kamera", frame)
        key = cv2.waitKey(1)
        if key == ord('b'):
            foto = frame.copy()
            tarih_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.6
            renk = (255, 255, 255)
            kalinlik = 1

            cv2.putText(foto, LOCATION, (10, foto.shape[0] - 10), font, font_scale, renk, kalinlik, cv2.LINE_AA)
            tarih_text_size = cv2.getTextSize(tarih_str, font, font_scale, kalinlik)[0]
            x_pos = foto.shape[1] - tarih_text_size[0] - 10
            y_pos = foto.shape[0] - 10
            cv2.putText(foto, tarih_str, (x_pos, y_pos), font, font_scale, renk, kalinlik, cv2.LINE_AA)

            filename = f"plate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            cv2.imwrite(filename, foto)
            print(f"Fotoğraf kaydedildi: {filename}")
            break
    cap.release()
    cv2.destroyAllWindows()
    return filename

def read_plate_text(image_path):
    with io.open(image_path, 'rb') as img_file:
        content = img_file.read()

    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations

    if not texts:
        return "PLAKA-YOK"

    all_text = texts[0].description.strip().replace(" ", "").upper()
    lines = all_text.splitlines()

    blacklist = ["TR", "TÜRKİYE", "GAZIANTEP", "GAZIEMIR", "TURKIYE"]
    for line in lines:
        cleaned = re.sub(r'[^A-Z0-9]', '', line)
        if any(bl in cleaned for bl in blacklist):
            continue
        if 5 <= len(cleaned) <= 10 and re.search(r'[A-Z]', cleaned) and re.search(r'\d', cleaned):
            return cleaned
    return "PLAKA-YOK"

def save_to_excel(photo_path, plate, weight, location):
    now = datetime.now()
    data = {
        "Tarih": [now.strftime("%Y-%m-%d")],
        "Saat": [now.strftime("%H:%M:%S")],
        "Plaka": [plate],
        "Agirlik (kg)": [weight],
        "Lokasyon": [location],
        "Fotoğraf Yolu": [photo_path]
    }
    if os.path.exists(EXCEL_FILE):
        df = pd.read_excel(EXCEL_FILE)
        df_new = pd.DataFrame(data)
        df = pd.concat([df, df_new], ignore_index=True)
    else:
        df = pd.DataFrame(data)
    df.to_excel(EXCEL_FILE, index=False)
    print(f"✅ Excel'e kaydedildi: {EXCEL_FILE}")

def send_state(state):
    if state == "TARTIM BİTTİ":
        state = "TARTIM_BITTI"
    message = f"{state}\n"
    arduino.write(message.encode())
    print(f"📤 Durum gönderildi: {state}")
    time.sleep(0.5)

def send_data(plate, weight):
    plate_ascii = turkce_to_ascii(plate)
    message = f"DATA:{plate_ascii}|{weight}\n"
    arduino.write(message.encode())
    print(f"📤 Veri gönderildi: {message.strip()}")
    time.sleep(0.5)

def tartim_akisi():
    send_state("TARTIM_YOK")
    print("🚦 Başlangıç bekleniyor...")

    while True:
        if arduino.in_waiting:
            gelen = arduino.readline().decode(errors='ignore').strip()
            if gelen:
                print(f"📥 Arduino'dan gelen: {gelen}")
                if gelen == "TARTIM":
                    print("✅ Konum doğru! Tartıma geçiliyor...")
                    image_path = capture_plate_image()
                    plate = read_plate_text(image_path)
                    weight = str(random.randint(15000, 32000))  # Tartım simülasyonu
                    print(f"🚚 Plaka: {plate}, Ağırlık: {weight} kg")
                    send_data(plate, weight)
                    send_state("TARTIM_BİTTİ")
                    save_to_excel(image_path, plate, weight, LOCATION)
                    break
        time.sleep(0.1)

def main():
    print("🟢 Tartım sistemi başlatıldı")
    tartim_akisi()

    while True:
        key = input("Tekrar tartım için 'b', çıkmak için 'q' basın: ").lower()
        if key == 'b':
            tartim_akisi()
        elif key == 'q':
            print("Çıkılıyor.")
            break

if __name__ == "__main__":
    main()
    