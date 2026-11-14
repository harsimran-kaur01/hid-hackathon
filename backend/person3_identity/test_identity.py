
import cv2
from pathlib import Path
from identity import get_recognizer, identify_face, enroll_person

# Get the current script folder
BASE_DIR = Path(__file__).parent

print("Loading recognizer...")
rec = get_recognizer()
print("Recognizer loaded successfully!\n")

# Load images
img1 = cv2.imread(str(BASE_DIR / "img1.jpeg"))
img2 = cv2.imread(str(BASE_DIR / "img2.jpeg"))
img3 = cv2.imread(str(BASE_DIR / "img3.jpeg"))

# Check images
if any(img is None for img in [img1, img2, img3]):
    raise FileNotFoundError("Check that img1.jpeg, img2.jpeg and img3.jpeg exist in this folder.")

print("All images loaded successfully!\n")

# Enroll two people
print("Enrolling people...")
print("Person A:", enroll_person("Person_A", img1))
print("Person B:", enroll_person("Person_B", img2))

# Identify enrolled person
print("\nTesting enrolled person:")
print(identify_face(img1))

# Identify a new person
print("\nTesting unknown person:")
print(identify_face(img3))

print("\nIdentity recognition test completed.")
