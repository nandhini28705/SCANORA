import os
import pytesseract
from PIL import Image, ImageStat, ImageFilter

INPUT_FOLDER = "../input"
OUTPUT_FOLDER = "../output"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

supported_formats = (".jpg", ".jpeg", ".png", ".bmp", ".webp")

images = [
    file for file in os.listdir(INPUT_FOLDER)
    if file.lower().endswith(supported_formats)
]

if not images:
    print("❌ No images found in input folder.")
    exit()

print("\n===================================")
print("       SCANORA IMAGE ANALYZER")
print("===================================")
print(f"Images found: {len(images)}")

for filename in images:

    print(f"\n🔍 Processing: {filename}")

    image_path = os.path.join(INPUT_FOLDER, filename)

    try:
        image = Image.open(image_path)

        # OCR
        text = pytesseract.image_to_string(image)

        # Image information
        width, height = image.size

        # Grayscale
        gray = image.convert("L")

        # Brightness
        brightness = ImageStat.Stat(gray).mean[0]

        # Sharpness
        edges = gray.filter(ImageFilter.FIND_EDGES)
        sharpness = ImageStat.Stat(edges).mean[0]

        # Quality
        if sharpness < 10:
            quality = "Blurry"
        elif sharpness < 25:
            quality = "Moderate"
        else:
            quality = "Sharp"

        # Lighting
        if brightness < 60:
            lighting = "Dark"
        elif brightness > 200:
            lighting = "Very Bright"
        else:
            lighting = "Good"

        # Score
        sharpness_score = min(sharpness * 4, 100)

        if 60 <= brightness <= 200:
            brightness_score = 100
        else:
            brightness_score = 50

        quality_score = (
            sharpness_score * 0.7
            + brightness_score * 0.3
        )

        # Recommendation
        if quality_score < 40:
            recommendation = "Retake image with better focus and clarity."
        elif quality_score < 70:
            recommendation = "Image is usable but can be improved."
        else:
            recommendation = "Image quality is good."

        # File names
        base_name = os.path.splitext(filename)[0]

        report_path = os.path.join(
            OUTPUT_FOLDER,
            f"{base_name}_report.txt"
        )

        ocr_path = os.path.join(
            OUTPUT_FOLDER,
            f"{base_name}_ocr.txt"
        )

        # Report
        report = f"""
--- SCANORA IMAGE QUALITY REPORT ---

Image Name      : {filename}
Image Size      : {width} x {height}
Brightness      : {brightness:.2f}
Sharpness       : {sharpness:.2f}
Quality         : {quality}
Lighting        : {lighting}
Quality Score   : {quality_score:.2f}/100

Recommendation  : {recommendation}

--- Extracted Text ---

{text}
"""

        # Save report
        with open(report_path, "w", encoding="utf-8") as file:
            file.write(report)

        # Save OCR
        with open(ocr_path, "w", encoding="utf-8") as file:
            file.write(text)

        print(f"   ✅ Quality: {quality}")
        print(f"   📊 Score: {quality_score:.2f}/100")
        print(f"   💡 Lighting: {lighting}")
        print(f"   📄 Report: {report_path}")

    except Exception as error:
        print(f"   ❌ Error: {error}")

print("\n===================================")
print("✅ SCANORA processing completed!")
print("📁 Check the output folder.")
print("===================================")