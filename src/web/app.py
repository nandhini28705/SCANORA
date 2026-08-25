from flask import (
    Flask,
    render_template,
    request,
    send_from_directory
)

from PIL import (
    Image,
    ImageStat,
    ImageFilter,
    ImageEnhance
)

import pytesseract
import os
import uuid
import json
from datetime import datetime
import textwrap

from werkzeug.utils import secure_filename

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


# =====================================
# FLASK APP
# =====================================

app = Flask(__name__)


# =====================================
# FOLDERS
# =====================================

BASE_DIR = os.path.abspath(
    os.path.dirname(__file__)
)

UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "uploads"
)

HISTORY_FILE = os.path.join(
    BASE_DIR,
    "analysis_history.json"
)


# =====================================
# ALLOWED IMAGE FORMATS
# =====================================

ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg"
}


app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# =====================================
# CREATE REQUIRED FOLDERS / FILES
# =====================================

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


if not os.path.exists(HISTORY_FILE):

    with open(
        HISTORY_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            [],
            file
        )


# =====================================
# CHECK ALLOWED FILE
# =====================================

def allowed_file(filename):

    return (
        "." in filename
        and filename.rsplit(
            ".",
            1
        )[1].lower()
        in ALLOWED_EXTENSIONS
    )


# =====================================
# LOAD HISTORY
# =====================================

def load_history():

    try:

        with open(
            HISTORY_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception:

        return []


# =====================================
# SAVE HISTORY
# =====================================

def save_history(history):

    with open(
        HISTORY_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            history,
            file,
            indent=4
        )


# =====================================
# ADD ANALYSIS TO HISTORY
# =====================================

def add_history(
    filename,
    data
):

    history = load_history()

    record = {

        "filename": filename,

        "date": datetime.now().strftime(
            "%d-%m-%Y %I:%M %p"
        ),

        "original_score": data["score"],

        "enhanced_score": None,

        "improvement": None,

        "improvement_percent": None,

        "quality": data["quality"]

    }

    history.insert(
        0,
        record
    )

    save_history(
        history
    )


# =====================================
# UPDATE ENHANCED HISTORY
# =====================================

def update_history(
    filename,
    enhanced_score,
    improvement,
    improvement_percent
):

    history = load_history()

    for record in history:

        if record["filename"] == filename:

            record["enhanced_score"] = enhanced_score

            record["improvement"] = round(
                improvement,
                2
            )

            record["improvement_percent"] = round(
                improvement_percent,
                2
            )

            break

    save_history(
        history
    )


# =====================================
# ANALYZE IMAGE
# =====================================

def analyze_image(image_path):

    image = Image.open(
        image_path
    ).convert(
        "RGB"
    )


    # =================================
    # IMAGE SIZE
    # =================================

    width, height = image.size


    # =================================
    # GRAYSCALE IMAGE
    # =================================

    gray = image.convert(
        "L"
    )


    # =================================
    # BRIGHTNESS
    # =================================

    brightness = ImageStat.Stat(
        gray
    ).mean[0]


    # =================================
    # SHARPNESS
    # =================================

    edges = gray.filter(
        ImageFilter.FIND_EDGES
    )

    sharpness = ImageStat.Stat(
        edges
    ).mean[0]


    # =================================
    # CONTRAST
    # =================================

    contrast = ImageStat.Stat(
        gray
    ).stddev[0]


    # =================================
    # QUALITY SCORE
    # =================================

    sharpness_score = min(
        sharpness * 4,
        100
    )


    if 60 <= brightness <= 200:

        brightness_score = 100

    else:

        brightness_score = 50


    contrast_score = min(
        contrast * 2,
        100
    )


    quality_score = (

        sharpness_score * 0.5

        + brightness_score * 0.2

        + contrast_score * 0.3

    )


    quality_score = min(
        quality_score,
        100
    )


    # =================================
    # QUALITY STATUS
    # =================================

    if quality_score < 40:

        quality = "Poor"

    elif quality_score < 70:

        quality = "Moderate"

    else:

        quality = "Good"


    # =================================
    # LIGHTING STATUS
    # =================================

    if brightness < 60:

        lighting = "Too Dark"

    elif brightness > 200:

        lighting = "Too Bright"

    else:

        lighting = "Good"


    # =================================
    # SHARPNESS STATUS
    # =================================

    if sharpness < 10:

        sharpness_status = "Low"

    elif sharpness < 20:

        sharpness_status = "Moderate"

    else:

        sharpness_status = "Good"


    # =================================
    # CONTRAST STATUS
    # =================================

    if contrast < 20:

        contrast_status = "Low"

    elif contrast < 40:

        contrast_status = "Moderate"

    else:

        contrast_status = "Good"


    # =================================
    # RESOLUTION STATUS
    # =================================

    pixels = width * height


    if pixels < 500000:

        resolution_status = "Low"

    elif pixels < 2000000:

        resolution_status = "Moderate"

    else:

        resolution_status = "High"


    # =================================
    # RETURN RESULTS
    # =================================

    return {

        "width": width,

        "height": height,

        "brightness": round(
            brightness,
            2
        ),

        "sharpness": round(
            sharpness,
            2
        ),

        "contrast": round(
            contrast,
            2
        ),

        "score": round(
            quality_score,
            2
        ),

        "quality": quality,

        "lighting": lighting,

        "sharpness_status": sharpness_status,

        "contrast_status": contrast_status,

        "resolution_status": resolution_status

    }


# =====================================
# HOME PAGE
# =====================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# =====================================
# HISTORY DASHBOARD
# =====================================

@app.route("/history")
def history():

    records = load_history()

    total_images = len(
        records
    )


    if total_images > 0:

        average_score = round(

            sum(
                record["original_score"]
                for record in records
            )
            /
            total_images,

            2

        )

    else:

        average_score = 0


    improved_images = len(

        [
            record
            for record in records
            if record["enhanced_score"] is not None
        ]

    )


    return render_template(

        "history.html",

        records=records,

        total_images=total_images,

        average_score=average_score,

        improved_images=improved_images

    )


# =====================================
# SERVE UPLOADED FILES
# =====================================

@app.route("/uploads/<filename>")
def uploaded_file(filename):

    return send_from_directory(

        app.config["UPLOAD_FOLDER"],

        filename

    )


# =====================================
# ANALYZE IMAGE
# =====================================

@app.route(
    "/analyze",
    methods=["POST"]
)
def analyze():


    # =================================
    # CHECK IMAGE
    # =================================

    if "image" not in request.files:

        return "No image uploaded"


    file = request.files["image"]


    if file.filename == "":

        return "No file selected"


    if not allowed_file(
        file.filename
    ):

        return (
            "Only JPG, JPEG and PNG "
            "images are allowed."
        )


    # =================================
    # CREATE UNIQUE FILENAME
    # =================================

    original_filename = secure_filename(
        file.filename
    )


    name, extension = os.path.splitext(
        original_filename
    )


    unique_id = uuid.uuid4().hex[:8]


    filename = (

        name

        + "_"

        + unique_id

        + extension

    )


    # =================================
    # IMAGE PATH
    # =================================

    image_path = os.path.join(

        app.config["UPLOAD_FOLDER"],

        filename

    )


    # =================================
    # SAVE IMAGE
    # =================================

    file.save(
        image_path
    )


    # =================================
    # ANALYZE IMAGE
    # =================================

    try:

        data = analyze_image(
            image_path
        )

    except Exception as error:

        print(
            "Image Analysis Error:",
            error
        )

        return "Invalid image file"


    # =================================
    # SAVE HISTORY
    # =================================

    add_history(

        filename,

        data

    )


    # =================================
    # OCR
    # =================================

    try:

        image = Image.open(
            image_path
        ).convert(
            "RGB"
        )


        text = pytesseract.image_to_string(

            image

        ).strip()


    except Exception as error:

        print(
            "OCR Error:",
            error
        )

        text = ""


    # =================================
    # SMART RECOMMENDATION
    # =================================

    if data["score"] < 40:

        recommendation = (

            "Image quality is poor. "

            "Retake the image with better "

            "focus, lighting and clarity."

        )


    elif data["score"] < 70:

        recommendation = (

            "Image is usable, but further "

            "improvement is recommended. "

            "Try improving focus and clarity."

        )


    else:

        recommendation = (

            "Image quality is good and "

            "suitable for OCR and further "

            "processing."

        )


    # =================================
    # RESULT PAGE
    # =================================

    return render_template(

        "result.html",

        filename=filename,

        width=data["width"],

        height=data["height"],

        brightness=data["brightness"],

        sharpness=data["sharpness"],

        contrast=data["contrast"],

        quality=data["quality"],

        quality_score=data["score"],

        lighting=data["lighting"],

        sharpness_status=data[
            "sharpness_status"
        ],

        contrast_status=data[
            "contrast_status"
        ],

        resolution_status=data[
            "resolution_status"
        ],

        text=text,

        recommendation=recommendation

    )


# =====================================
# ENHANCE IMAGE
# =====================================

@app.route(
    "/enhance",
    methods=["POST"]
)
def enhance():


    filename = request.form.get(
        "filename"
    )


    if not filename:

        return "No image selected"


    image_path = os.path.join(

        app.config["UPLOAD_FOLDER"],

        filename

    )


    if not os.path.exists(
        image_path
    ):

        return "Image not found"


    # =================================
    # OPEN IMAGE
    # =================================

    try:

        image = Image.open(
            image_path
        ).convert(
            "RGB"
        )

    except Exception:

        return "Unable to open image"


    # =================================
    # ENHANCE SHARPNESS
    # =================================

    enhanced = ImageEnhance.Sharpness(

        image

    ).enhance(
        2.5
    )


    # =================================
    # ENHANCE CONTRAST
    # =================================

    enhanced = ImageEnhance.Contrast(

        enhanced

    ).enhance(
        1.2
    )


    # =================================
    # APPLY SHARPEN FILTER
    # =================================

    enhanced = enhanced.filter(

        ImageFilter.SHARPEN

    )


    # =================================
    # ENHANCED FILENAME
    # =================================

    enhanced_filename = (

        "enhanced_"

        + filename

    )


    enhanced_path = os.path.join(

        app.config["UPLOAD_FOLDER"],

        enhanced_filename

    )


    # =================================
    # SAVE ENHANCED IMAGE
    # =================================

    try:

        enhanced.save(

            enhanced_path,

            quality=95

        )

    except Exception as error:

        print(
            "Enhancement Save Error:",
            error
        )

        return "Unable to save enhanced image"


    # =================================
    # ANALYZE ORIGINAL
    # =================================

    original_data = analyze_image(

        image_path

    )


    # =================================
    # ANALYZE ENHANCED
    # =================================

    enhanced_data = analyze_image(

        enhanced_path

    )


    # =================================
    # CALCULATE IMPROVEMENT
    # =================================

    improvement = (

        enhanced_data["score"]

        -

        original_data["score"]

    )


    if original_data["score"] > 0:

        improvement_percent = (

            improvement

            /

            original_data["score"]

        ) * 100

    else:

        improvement_percent = 0


    improvement = round(
        improvement,
        2
    )


    improvement_percent = round(
        improvement_percent,
        2
    )


    # =================================
    # UPDATE HISTORY
    # =================================

    update_history(

        filename,

        enhanced_data["score"],

        improvement,

        improvement_percent

    )


    # =================================
    # SHOW ENHANCED PAGE
    # =================================

    return render_template(

        "enhanced.html",

        original_filename=filename,

        enhanced_filename=enhanced_filename,

        original_brightness=original_data[
            "brightness"
        ],

        original_sharpness=original_data[
            "sharpness"
        ],

        original_contrast=original_data[
            "contrast"
        ],

        original_score=original_data[
            "score"
        ],

        enhanced_brightness=enhanced_data[
            "brightness"
        ],

        enhanced_sharpness=enhanced_data[
            "sharpness"
        ],

        enhanced_contrast=enhanced_data[
            "contrast"
        ],

        enhanced_score=enhanced_data[
            "score"
        ],

        improvement=improvement,

        improvement_percent=improvement_percent

    )


# =====================================
# FINAL REPORT PAGE
# =====================================

@app.route(
    "/report",
    methods=["POST"]
)
def report():


    filename = request.form.get(
        "filename"
    )


    enhanced_filename = request.form.get(
        "enhanced_filename"
    )


    if not filename:

        return "Original image not found"


    if not enhanced_filename:

        return "Enhanced image not found"


    original_path = os.path.join(

        app.config["UPLOAD_FOLDER"],

        filename

    )


    enhanced_path = os.path.join(

        app.config["UPLOAD_FOLDER"],

        enhanced_filename

    )


    if not os.path.exists(
        original_path
    ):

        return "Original image not found"


    if not os.path.exists(
        enhanced_path
    ):

        return "Enhanced image not found"


    # =================================
    # ANALYZE BOTH IMAGES
    # =================================

    original_data = analyze_image(

        original_path

    )


    enhanced_data = analyze_image(

        enhanced_path

    )


    # =================================
    # IMPROVEMENT
    # =================================

    improvement = (

        enhanced_data["score"]

        -

        original_data["score"]

    )


    if original_data["score"] > 0:

        improvement_percent = (

            improvement

            /

            original_data["score"]

        ) * 100

    else:

        improvement_percent = 0


    improvement = round(
        improvement,
        2
    )


    improvement_percent = round(
        improvement_percent,
        2
    )


    # =================================
    # OCR
    # =================================

    try:

        enhanced_image = Image.open(

            enhanced_path

        ).convert(
            "RGB"
        )


        text = pytesseract.image_to_string(

            enhanced_image

        ).strip()


    except Exception as error:

        print(
            "OCR Error:",
            error
        )

        text = ""


    # =================================
    # RECOMMENDATION
    # =================================

    if enhanced_data["score"] >= 70:

        recommendation = (

            "Overall image quality is good "

            "and suitable for further processing."

        )


    elif enhanced_data["score"] >= 40:

        recommendation = (

            "Image quality is moderate. "

            "Further enhancement may improve "

            "clarity and OCR performance."

        )


    else:

        recommendation = (

            "Image quality is still low. "

            "Try using a clearer image with "

            "better focus and lighting."

        )


    # =================================
    # SHOW REPORT
    # =================================

    return render_template(

        "report.html",

        filename=filename,

        width=original_data["width"],

        height=original_data["height"],

        original_brightness=original_data[
            "brightness"
        ],

        original_sharpness=original_data[
            "sharpness"
        ],

        original_contrast=original_data[
            "contrast"
        ],

        original_score=original_data[
            "score"
        ],

        enhanced_brightness=enhanced_data[
            "brightness"
        ],

        enhanced_sharpness=enhanced_data[
            "sharpness"
        ],

        enhanced_contrast=enhanced_data[
            "contrast"
        ],

        enhanced_score=enhanced_data[
            "score"
        ],

        improvement=improvement,

        improvement_percent=improvement_percent,

        text=text,

        recommendation=recommendation

    )


# =====================================
# DOWNLOAD PDF REPORT
# =====================================

@app.route(
    "/download-report",
    methods=["POST"]
)
def download_report():


    filename = request.form.get(

        "filename",

        "Unknown Image"

    )


    width = request.form.get(

        "width",

        "N/A"

    )


    height = request.form.get(

        "height",

        "N/A"

    )


    original_brightness = request.form.get(

        "original_brightness",

        "N/A"

    )


    original_sharpness = request.form.get(

        "original_sharpness",

        "N/A"

    )


    original_contrast = request.form.get(

        "original_contrast",

        "N/A"

    )


    original_score = request.form.get(

        "original_score",

        "N/A"

    )


    enhanced_brightness = request.form.get(

        "enhanced_brightness",

        "N/A"

    )


    enhanced_sharpness = request.form.get(

        "enhanced_sharpness",

        "N/A"

    )


    enhanced_contrast = request.form.get(

        "enhanced_contrast",

        "N/A"

    )


    enhanced_score = request.form.get(

        "enhanced_score",

        "N/A"

    )


    improvement = request.form.get(

        "improvement",

        "N/A"

    )


    improvement_percent = request.form.get(

        "improvement_percent",

        "N/A"

    )


    text = request.form.get(

        "text",

        ""

    )


    recommendation = request.form.get(

        "recommendation",

        "N/A"

    )


    # =================================
    # PDF FILE
    # =================================

    pdf_filename = (

        "SCANORA_Final_Report.pdf"

    )


    pdf_path = os.path.join(

        app.config["UPLOAD_FOLDER"],

        pdf_filename

    )


    # =================================
    # CREATE PDF
    # =================================

    pdf = canvas.Canvas(

        pdf_path,

        pagesize=A4

    )


    page_width, page_height = A4


    y = page_height - 50


    # =================================
    # CHECK PAGE SPACE
    # =================================

    def check_page_space():

        nonlocal y


        if y < 80:

            pdf.showPage()

            y = page_height - 50


    # =================================
    # ADD TITLE
    # =================================

    def add_title(title):

        nonlocal y


        check_page_space()


        pdf.setFont(

            "Helvetica-Bold",

            15

        )


        pdf.drawString(

            50,

            y,

            title

        )


        y -= 25


    # =================================
    # ADD WRAPPED TEXT
    # =================================

    def add_wrapped_line(
        label,
        value
    ):

        nonlocal y


        check_page_space()


        pdf.setFont(

            "Helvetica",

            11

        )


        full_text = (

            f"{label}: {value}"

        )


        wrapped_lines = textwrap.wrap(

            full_text,

            width=85

        )


        for line in wrapped_lines:

            check_page_space()


            pdf.drawString(

                60,

                y,

                line

            )


            y -= 18


    # =================================
    # PDF HEADER
    # =================================

    pdf.setFont(

        "Helvetica-Bold",

        22

    )


    pdf.drawCentredString(

        page_width / 2,

        y,

        "SCANORA FINAL REPORT"

    )


    y -= 30


    pdf.setFont(

        "Helvetica",

        11

    )


    pdf.drawCentredString(

        page_width / 2,

        y,

        "Smart Image Quality Analysis and OCR System"

    )


    y -= 50


    # =================================
    # IMAGE INFORMATION
    # =================================

    add_title(

        "Image Information"

    )


    add_wrapped_line(

        "Original Image",

        filename

    )


    add_wrapped_line(

        "Image Size",

        f"{width} x {height}"

    )


    y -= 10


    # =================================
    # ORIGINAL ANALYSIS
    # =================================

    add_title(

        "Original Image Analysis"

    )


    add_wrapped_line(

        "Brightness",

        original_brightness

    )


    add_wrapped_line(

        "Sharpness",

        original_sharpness

    )


    add_wrapped_line(

        "Contrast",

        original_contrast

    )


    add_wrapped_line(

        "Quality Score",

        f"{original_score}/100"

    )


    y -= 10


    # =================================
    # ENHANCED ANALYSIS
    # =================================

    add_title(

        "Enhanced Image Analysis"

    )


    add_wrapped_line(

        "Brightness",

        enhanced_brightness

    )


    add_wrapped_line(

        "Sharpness",

        enhanced_sharpness

    )


    add_wrapped_line(

        "Contrast",

        enhanced_contrast

    )


    add_wrapped_line(

        "Quality Score",

        f"{enhanced_score}/100"

    )


    y -= 10


    # =================================
    # QUALITY IMPROVEMENT
    # =================================

    add_title(

        "Quality Improvement"

    )


    add_wrapped_line(

        "Improvement",

        f"{improvement} points"

    )


    add_wrapped_line(

        "Improvement Percentage",

        f"{improvement_percent}%"

    )


    y -= 10


    # =================================
    # OCR RESULT
    # =================================

    add_title(

        "OCR Result"

    )


    if text.strip():

        add_wrapped_line(

            "Result",

            text

        )

    else:

        add_wrapped_line(

            "Result",

            "No text detected."

        )


    y -= 10


    # =================================
    # RECOMMENDATION
    # =================================

    add_title(

        "Smart Recommendation"

    )


    add_wrapped_line(

        "Recommendation",

        recommendation

    )


    # =================================
    # FOOTER
    # =================================

    pdf.setFont(

        "Helvetica",

        9

    )


    pdf.drawCentredString(

        page_width / 2,

        35,

        "Generated by SCANORA"

    )


    # =================================
    # SAVE PDF
    # =================================

    pdf.save()


    # =================================
    # DOWNLOAD PDF
    # =================================

    return send_from_directory(

        app.config["UPLOAD_FOLDER"],

        pdf_filename,

        as_attachment=True

    )


# =====================================
# RUN FLASK APP
# =====================================

if __name__ == "__main__":

    app.run(

        debug=True

    )