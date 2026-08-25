import pytesseract
from PIL import Image


original_path = "../input/test.jpg"
enhanced_path = "../output/enhanced_test.jpg"


# Original image OCR
original_image = Image.open(original_path)
original_text = pytesseract.image_to_string(original_image).strip()


# Enhanced image OCR
enhanced_image = Image.open(enhanced_path)
enhanced_text = pytesseract.image_to_string(enhanced_image).strip()


print("\n===================================")
print("       SCANORA OCR COMPARISON")
print("===================================")

print("\nORIGINAL IMAGE TEXT")
print("-----------------------------------")
print(original_text if original_text else "[No text detected]")


print("\nENHANCED IMAGE TEXT")
print("-----------------------------------")
print(enhanced_text if enhanced_text else "[No text detected]")


# Save comparison
output_path = "../output/ocr_comparison.txt"

comparison = f"""
--- SCANORA OCR COMPARISON ---

ORIGINAL IMAGE TEXT
-------------------
{original_text if original_text else "[No text detected]"}

ENHANCED IMAGE TEXT
-------------------
{enhanced_text if enhanced_text else "[No text detected]"}
"""

with open(output_path, "w", encoding="utf-8") as file:
    file.write(comparison)


print("\n===================================")
print("✅ OCR comparison completed!")
print(f"📄 Saved to: {output_path}")
print("===================================")