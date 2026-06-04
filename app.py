
from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io

app = Flask(__name__)

df = pd.read_excel("exam.xlsx")
df.columns = [c.strip() for c in df.columns]

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/search")
def search():
    enrlno = request.args.get("enrlno","").strip()

    if not enrlno:
        return jsonify({"error":"Enter ENRLNO"}), 400

    res = df[df["ENRLNO"].astype(str).str.strip() == enrlno]

    if res.empty:
        return jsonify({"error":"No record found"}), 404

    return jsonify(res.iloc[0].to_dict())


@app.route("/download")
def download():
    enrlno = request.args.get("enrlno","").strip()

    res = df[df["ENRLNO"].astype(str).str.strip() == enrlno]
    if res.empty:
        return "No record found", 404

    data = res.iloc[0].to_dict()

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)

    y = 800
    p.setFont("Helvetica-Bold", 14)
    p.drawString(200, y, "STUDENT EXAM RESULT")
    y -= 40

    p.setFont("Helvetica", 10)

    for k, v in data.items():
        p.drawString(50, y, f"{k}: {v}")
        y -= 20
        if y < 50:
            p.showPage()
            y = 800

    p.save()
    buffer.seek(0)

    return send_file(buffer, as_attachment=True,
                     download_name=f"{enrlno}_result.pdf",
                     mimetype="application/pdf")


if __name__ == "__main__":
    app.run(debug=True)
