from PIL import Image, ImageStat, ImageFilter
import os


def analyze_image(image_path):

    image = Image.open(image_path).convert("RGB")

    width, height = image.size

    gray = image.convert("L")

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

    if 60 <= brightness <= 200:
        brightness_score = 100
    else:
        brightness_score = 50

    score = (
        sharpness_score * 0.7
        + brightness_score * 0.3
    )

    return width, height, brightness, sharpness, quality, lighting, score


original = "../input/test.jpg"
enhanced = "../output/enhanced_test.jpg"

original_data = analyze_image(original)
enhanced_data = analyze_image(enhanced)


print("\n===================================")
print("       SCANORA QUALITY COMPARISON")
print("===================================")

print("\nORIGINAL IMAGE")
print("-----------------------------------")
print(f"Size       : {original_data[0]} x {original_data[1]}")
print(f"Brightness : {original_data[2]:.2f}")
print(f"Sharpness  : {original_data[3]:.2f}")
print(f"Quality    : {original_data[4]}")
print(f"Lighting   : {original_data[5]}")
print(f"Score      : {original_data[6]:.2f}/100")


print("\nENHANCED IMAGE")
print("-----------------------------------")
print(f"Size       : {enhanced_data[0]} x {enhanced_data[1]}")
print(f"Brightness : {enhanced_data[2]:.2f}")
print(f"Sharpness  : {enhanced_data[3]:.2f}")
print(f"Quality    : {enhanced_data[4]}")
print(f"Lighting   : {enhanced_data[5]}")
print(f"Score      : {enhanced_data[6]:.2f}/100")


improvement = enhanced_data[6] - original_data[6]

print("\n===================================")
print(f"Quality Improvement : {improvement:.2f} points")

if improvement > 0:
    print("✅ Image quality improved.")
else:
    print("ℹ️ No significant improvement detected.")

print("===================================")