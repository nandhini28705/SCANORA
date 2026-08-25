from PIL import Image, ImageStat, ImageFilter

# Input image
image_path = "../input/test.jpg"

# Output report
output_path = "../output/quality_report.txt"

# Open image
image = Image.open(image_path)

# Image dimensions
width, height = image.size

# Convert to grayscale
gray_image = image.convert("L")

# Brightness
brightness = ImageStat.Stat(gray_image).mean[0]

# Sharpness
edges = gray_image.filter(ImageFilter.FIND_EDGES)
sharpness = ImageStat.Stat(edges).mean[0]

# Quality classification
if sharpness < 10:
    quality = "Blurry"
elif sharpness < 25:
    quality = "Moderate"
else:
    quality = "Sharp"

# Lighting classification
if brightness < 60:
    lighting = "Dark"
elif brightness > 200:
    lighting = "Very Bright"
else:
    lighting = "Good"

# Calculate quality score
sharpness_score = min(sharpness * 4, 100)

if 60 <= brightness <= 200:
    brightness_score = 100
else:
    brightness_score = 50

quality_score = (sharpness_score * 0.7) + (brightness_score * 0.3)

# Recommendation
if quality_score < 40:
    recommendation = "Retake image with better focus and clarity."
elif quality_score < 70:
    recommendation = "Image is usable but can be improved."
else:
    recommendation = "Image quality is good."

# Create report
report = f"""
--- SCANORA Image Quality Report ---

Image Size      : {width} x {height}
Brightness      : {brightness:.2f}
Sharpness       : {sharpness:.2f}
Quality         : {quality}
Lighting        : {lighting}
Quality Score   : {quality_score:.2f}/100

Recommendation  : {recommendation}
"""

print(report)

# Save report
with open(output_path, "w", encoding="utf-8") as file:
    file.write(report)

print(f"✅ Report saved to: {output_path}")