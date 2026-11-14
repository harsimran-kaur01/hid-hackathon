import cv2, numpy as np, requests
from spoof_detector import detect_spoof


def load_url(url):
    resp = requests.get(url)
    arr = np.asarray(bytearray(resp.content), dtype=np.uint8)
    return cv2.imdecode(arr, cv2.IMREAD_COLOR)


genuine = load_url(
    "https://raw.githubusercontent.com/spearb0lt/Face-Liveliness-Detection-Using-DL/main/dataset/real/1604.png"
)
spoof = load_url(
    "https://raw.githubusercontent.com/spearb0lt/Face-Liveliness-Detection-Using-DL/main/dataset/fake/2464.png"
)

print("Genuine:", detect_spoof(genuine, return_evidence=True))
print("Spoof:  ", detect_spoof(spoof, return_evidence=True))
