import pytesseract
from PIL import Image
import os

# Input image path
image_path = "../input/test.jpg"

# Output text file path
output_path = "../output/result.txt"

# Open image
image = Image.open(image_path)

# Extract text using OCR
text = pytesseract.image_to_string(image)

# Save extracted text
with open(output_path, "w", encoding="utf-8") as file:
    file.write(text)

print("\n--- Extracted Text ---\n")
print(text)

print("\n✅ OCR result saved to:", output_path)