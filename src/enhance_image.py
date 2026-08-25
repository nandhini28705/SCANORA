from PIL import Image, ImageEnhance, ImageFilter
import os

input_path = "../input/test.jpg"
output_path = "../output/enhanced_test.jpg"

# Open image
image = Image.open(input_path)
image = image.convert("RGB")

# Improve sharpness
enhanced = ImageEnhance.Sharpness(image).enhance(2.5)

# Improve contrast
enhanced = ImageEnhance.Contrast(enhanced).enhance(1.2)

# Apply slight sharpening filter
enhanced = enhanced.filter(ImageFilter.SHARPEN)

# Save enhanced image
enhanced.save(output_path, quality=95)

print("===================================")
print("       SCANORA IMAGE ENHANCEMENT")
print("===================================")
print("Original :", input_path)
print("Enhanced :", output_path)
print("✅ Enhanced image created successfully!")