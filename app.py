from flask import Flask, request, jsonify, send_file
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

app = Flask(__name__)

# Function to generate PDF for questions
def generate_questions_pdf(data, filename="trivia_questions.pdf"):
    pdf_path = os.path.join("pdfs", filename)
    os.makedirs("pdfs", exist_ok=True)
    
    c = canvas.Canvas(pdf_path, pagesize=letter)
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
            
            y_position -= 10  # Space after each question
            
            if y_position < 50:  # Create a new page if needed
                c.showPage()
                y_position = 750
    
    c.save()
    return pdf_path

# Function to generate PDF with answers & explanations
def generate_answers_pdf(data, filename="trivia_answers.pdf"):
    pdf_path = os.path.join("pdfs", filename)
    os.makedirs("pdfs", exist_ok=True)
    
    c = canvas.Canvas(pdf_path, pagesize=letter)
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
            y_position -= 40  # Space after each question
            
            if y_position < 50:  # Create a new page if needed
                c.showPage()
                y_position = 750
    
    c.save()
    return pdf_path

@app.route("/generate-pdf", methods=["POST"])
def generate_pdf():
    """API endpoint to generate PDFs from JSON input."""
    data = request.get_json()
    print("Hi This is your data:", data)
    
    if not data or "trivia_questions" not in data:
        return jsonify({"error": "Invalid JSON format"}), 400
    
    questions_pdf = generate_questions_pdf(data)
    print(questions_pdf)
    answers_pdf = generate_answers_pdf(data)
    print(answers_pdf)
    
    return jsonify({
        "message": "PDFs generated successfully",
        "questions_pdf": f"https://921e-2603-8080-2000-ea3-30e7-d7c9-f509-c3f1.ngrok-free.app/download/questions",
        "answers_pdf": f"https://921e-2603-8080-2000-ea3-30e7-d7c9-f509-c3f1.ngrok-free.app/download/answers"
    })

@app.route("/download/questions", methods=["GET"])
def download_questions_pdf():
    """Download Questions PDF."""
    pdf_path = os.path.join("pdfs", "trivia_questions.pdf")
    return send_file(pdf_path, as_attachment=True)

@app.route("/download/answers", methods=["GET"])
def download_answers_pdf():
    """Download Answers PDF."""
    pdf_path = os.path.join("pdfs", "trivia_answers.pdf")
    return send_file(pdf_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
