import cv2
from identity import get_recognizer, identify_face, enroll_person

print("Loading recognizer...")
rec = get_recognizer()
print("Ready!\n")

# ========== HOW TO USE ==========
# 1. Put some clear face photos in this folder (or give full path)
# 2. Change the filenames below to your actual image names

# Example enrollment (uncomment and change paths when you have images)
# enroll_person("Alice", cv2.imread("alice.jpg"))
# enroll_person("Bob",   cv2.imread("bob.jpg"))

# Example identification
# result = identify_face(cv2.imread("test.jpg"))
# print(result)

print("Module is ready.")
print("To enroll someone:")
print('  enroll_person("Name", cv2.imread("photo.jpg"))')
print()
print("To identify a face:")
print('  result = identify_face(cv2.imread("photo.jpg"))')
print('  print(result)')