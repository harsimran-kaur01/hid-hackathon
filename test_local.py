# test_local.py
import cv2
import numpy as np
import requests
from spoof_detector import detect_spoof


def load_image_from_url(url):
    response = requests.get(url)
    image_array = np.asarray(bytearray(response.content), dtype=np.uint8)
    return cv2.imdecode(image_array, cv2.IMREAD_COLOR)


print("Loading images from URLs...")

# Genuine face sample
genuine_url = "https://raw.githubusercontent.com/spearb0lt/Face-Liveliness-Detection-Using-DL/main/dataset/real/1604.png"
genuine_img = load_image_from_url(genuine_url)

# Spoof face sample
spoof_url = "https://raw.githubusercontent.com/spearb0lt/Face-Liveliness-Detection-Using-DL/main/dataset/fake/2464.png"
spoof_img = load_image_from_url(spoof_url)

print("\n--- Testing Genuine Image ---")
result_genuine = detect_spoof(genuine_img, return_evidence=True)
print(result_genuine)

print("\n--- Testing Spoof Image ---")
result_spoof = detect_spoof(spoof_img, return_evidence=True)
print(result_spoof)
