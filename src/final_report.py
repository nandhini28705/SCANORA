from PIL import Image, ImageStat, ImageFilter
import pytesseract


original_path = "../input/test.jpg"
enhanced_path = "../output/enhanced_test.jpg"
report_path = "../output/SCANORA_Final_Report.txt"


def analyze_image(path):

    image = Image.open(path).convert("RGB")
    gray = image.convert("L")

    width, height = image.size

    brightness = ImageStat.Stat(gray).mean[0]

    edges = gray.filter(ImageFilter.FIND_EDGES)
    sharpness = ImageStat.Stat(edges).mean[0]

    if sharpness < 10:
        quality = "Blurry"
    elif sharpness < 25:
        quality = "Moderate"
    else:
        quality = "Sharp"

    if brightness < 60:
        lighting = "Dark"
    elif brightness > 200:
        lighting = "Very Bright"
    else:
        lighting = "Good"

    sharpness_score = min(sharpness * 4, 100)

    brightness_score = (
        100 if 60 <= brightness <= 200 else 50
    )

    score = (
        sharpness_score * 0.7
        + brightness_score * 0.3
    )

    return {
        "width": width,
        "height": height,
        "brightness": brightness,
        "sharpness": sharpness,
        "quality": quality,
        "lighting": lighting,
        "score": score
    }


# Analyze images
original = analyze_image(original_path)
enhanced = analyze_image(enhanced_path)


# OCR
original_text = pytesseract.image_to_string(
    Image.open(original_path)
).strip()

enhanced_text = pytesseract.image_to_string(
    Image.open(enhanced_path)
).strip()


# Improvement
improvement = enhanced["score"] - original["score"]


# Recommendation
if enhanced["score"] >= 70:
    recommendation = "Image quality is good and suitable for OCR."
elif enhanced["score"] >= 40:
    recommendation = "Image is usable but further improvement is recommended."
else:
    recommendation = "Image is still low quality. Retake with better focus and lighting."


# Final report
report = f"""
========================================
        SCANORA FINAL REPORT
========================================

ORIGINAL IMAGE
----------------------------------------

Image Size      : {original["width"]} x {original["height"]}
Brightness      : {original["brightness"]:.2f}
Sharpness       : {original["sharpness"]:.2f}
Quality         : {original["quality"]}
Lighting        : {original["lighting"]}
Quality Score   : {original["score"]:.2f}/100


ENHANCED IMAGE
----------------------------------------

Image Size      : {enhanced["width"]} x {enhanced["height"]}
Brightness      : {enhanced["brightness"]:.2f}
Sharpness       : {enhanced["sharpness"]:.2f}
Quality         : {enhanced["quality"]}
Lighting        : {enhanced["lighting"]}
Quality Score   : {enhanced["score"]:.2f}/100


QUALITY IMPROVEMENT
----------------------------------------

Improvement     : {improvement:.2f} points


ORIGINAL OCR
----------------------------------------

{original_text if original_text else "[No text detected]"}


ENHANCED OCR
----------------------------------------

{enhanced_text if enhanced_text else "[No text detected]"}


FINAL RECOMMENDATION
----------------------------------------

{recommendation}


========================================
       SCANORA ANALYSIS COMPLETED
========================================
"""


print(report)


with open(report_path, "w", encoding="utf-8") as file:
    file.write(report)


print(f"✅ Final report saved to: {report_path}")