from flask import Flask, request, jsonify
from google.cloud import storage
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
import uuid

# Set Google Application Credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "gcs-key.json"

app = Flask(__name__)

# Google Cloud Storage Configuration
BUCKET_NAME = "my-trivia-pdfs"

# Initialize Google Cloud Storage Client
storage_client = storage.Client()

def generate_unique_folder():
    """Generates a unique folder name using UUID."""
    return f"trivia_{uuid.uuid4().hex[:8]}"  # Creates a folder like 'trivia_3f5a9b8c'

def upload_to_gcs(local_path, folder_name, gcs_filename):
    """Uploads a file to Google Cloud Storage inside a unique folder."""
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(f"{folder_name}/{gcs_filename}")  # Store inside the unique folder
    blob.upload_from_filename(local_path)
    return f"https://storage.googleapis.com/{BUCKET_NAME}/{folder_name}/{gcs_filename}"

def generate_questions_pdf(data, folder_name, filename="trivia_questions.pdf"):
    """Generates Questions PDF and uploads it to GCS inside the folder."""
    local_path = os.path.join("/tmp", filename)
    c = canvas.Canvas(local_path, pagesize=letter)
    y_position = 750

    for item in data["trivia_questions"]:
        concept = item["concept"]
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y_position, f"Concept: {concept}")
        y_position -= 20

        for q in item["questions"]:
            c.setFont("Helvetica", 12)
            c.drawString(50, y_position, f"Question: {q['question']}")
            y_position -= 20

            for choice in q["choices"]:
                c.drawString(70, y_position, f"- {choice}")
                y_position -= 15

            y_position -= 10

            if y_position < 50:
                c.showPage()
                y_position = 750

    c.save()
    return upload_to_gcs(local_path, folder_name, filename)

def generate_answers_pdf(data, folder_name, filename="trivia_answers.pdf"):
    """Generates Answers PDF and uploads it to GCS inside the folder."""
    local_path = os.path.join("/tmp", filename)
    c = canvas.Canvas(local_path, pagesize=letter)
    y_position = 750

    for item in data["trivia_questions"]:
        concept = item["concept"]
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y_position, f"Concept: {concept}")
        y_position -= 20

        for q in item["questions"]:
            c.setFont("Helvetica", 12)
            c.drawString(50, y_position, f"Question: {q['question']}")
            y_position -= 20
            c.drawString(50, y_position, f"Correct Answer: {q['correct_answer']}")
            y_position -= 20
            c.drawString(50, y_position, f"Explanation: {q['explanation']}")
            y_position -= 40

            if y_position < 50:
                c.showPage()
                y_position = 750

    c.save()
    return upload_to_gcs(local_path, folder_name, filename)

@app.route("/generate-pdf", methods=["POST"])
def generate_pdf():
    """Generates PDFs, uploads them to GCS inside a unique folder, and returns URLs."""
    data = request.get_json()

    if not data or "trivia_questions" not in data:
        return jsonify({"error": "Invalid JSON format"}), 400

    # Create a unique folder name
    folder_name = generate_unique_folder()

    questions_pdf_url = generate_questions_pdf(data, folder_name)
    answers_pdf_url = generate_answers_pdf(data, folder_name)

    return jsonify({
        "message": "PDFs generated successfully",
        "folder": folder_name,
        "questions_pdf": questions_pdf_url,
        "answers_pdf": answers_pdf_url
    })

if __name__ == "__main__":
    app.run(debug=True)
