
import cv2 as cv
import numpy as np
import os
import time
import keyboard
from ctypes import windll
from windowcapture import WindowCapture
from roboflow import Roboflow

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Roboflow modelini başlat
rf = Roboflow(api_key="kxjFczwLbFhVnnWyl34j")
project = rf.workspace("efrah").project("cs-go-2-terrorist-attacker")
model = project.version(1).model

def detect_objects_with_yolo(image):
    image_rgb = cv.cvtColor(image, cv.COLOR_BGR2RGB)
    temp_image_path = "temp_image.jpg"
    cv.imwrite(temp_image_path, image_rgb)
    prediction = model.predict(temp_image_path)
    results = prediction.json()['predictions']
    return results

def findClickPositions_with_yolo(image, threshold=0.6, debug_mode=None):
    results = detect_objects_with_yolo(image)
    points = []
    for result in results:
        if result['confidence'] >= threshold:
            x = result['x']
            y = result['y']
            width = result['width']
            height = result['height']
            center_x = int(x)
            center_y = int(y)
            points.append((center_x, center_y))
            if debug_mode == 'rectangles':
                top_left = (int(x - width / 2), int(y - height / 2))
                bottom_right = (int(x + width / 2), int(y + height / 2))
                cv.rectangle(image, top_left, bottom_right, color=(0, 255, 0), thickness=2)
            elif debug_mode == 'points':
                cv.drawMarker(image, (center_x, center_y), color=(255, 0, 255), markerType=cv.MARKER_CROSS, markerSize=20, thickness=2)
    return points

header = "Counter-Strike 2"
wincap = WindowCapture(header)

dd_dll = windll.LoadLibrary("C:/Users/Jeefrah/Downloads/master-master/master-master/dd40605x64.dll")

while not keyboard.is_pressed('q'):
    try:
        start_time = time.time()
        
        # Ekran görüntüsü al
        screen = wincap.get_screenshot()

        # YOLO ile nesne tespiti yap
        objectPoints = findClickPositions_with_yolo(screen, threshold=0.6, debug_mode='rectangles')
        print("Nesne koordinatları:", objectPoints)

        # Ekran merkezindeki crosshair'in koordinatlarını hesapla
        screen_height, screen_width, _ = screen.shape
        crosshair_x = screen_width // 2
        crosshair_y = screen_height // 2

        # Tespit edilen nesnelerin koordinatlarına doğru fareyi hareket ettir ve tıkla
        for x, y in objectPoints:
            delta_x = x - crosshair_x
            delta_y = y - crosshair_y

            dd_dll.DD_movR(int(delta_x+100), int(delta_y+10))  # Göreceli hareket kullan

            # Fare tıklama işlemi
            dd_dll.DD_btn(1)  # Sol tıklama
            dd_dll.DD_btn(2)  # Sol tıklamayı bırak

        st = dd_dll.DD_btn(0)  # DD Initialize
        if st == 1:
            print("Tamam")

        # 20 ms (0.02 saniye) bekle
        elapsed_time = time.time() - start_time
        if elapsed_time < 0.02:
            time.sleep(0.02 - elapsed_time)

    except Exception as e:
        print(f"Bir hata oluştu: {e}")
