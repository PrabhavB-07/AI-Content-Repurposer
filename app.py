from flask import Flask, render_template, request, jsonify, send_file
import io
from utils.generator import generate_content
from utils.export import generate_pdf, generate_docx

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    try:
        data       = request.get_json()
        user_input = data.get("url")
        tone       = data.get("tone")
        result     = generate_content(user_input, tone)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"result": f"ERROR: {str(e)}"})


@app.route("/export/pdf", methods=["POST"])
def export_pdf():
    try:
        data    = request.get_json()
        content = data.get("content", "")
        pdf_bytes = generate_pdf(content)
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype="application/pdf",
            as_attachment=True,
            download_name="generated-content.pdf",
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/export/docx", methods=["POST"])
def export_docx():
    try:
        data    = request.get_json()
        content = data.get("content", "")
        docx_bytes = generate_docx(content)
        return send_file(
            io.BytesIO(docx_bytes),
            mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            as_attachment=True,
            download_name="generated-content.docx",
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)