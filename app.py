from asr_model import transcribe_audio
from summarizer_model import summarize_text
from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
import os
from werkzeug.utils import secure_filename
from flask import send_file
import json

app = Flask(__name__)
app.secret_key = "secretkey"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# MySQL connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Sh@nvi#8877",
    database="transcribeflow"
)

# Home = Login Page
@app.route('/')
def home():
    return render_template("login.html")

# Register Page
@app.route('/register_page')
def register_page():
    return render_template("register.html")

# Register Logic
@app.route('/register', methods=['POST'])
def register():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']

    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
        (name, email, password)
    )
    conn.commit()
    cursor.close()

    return redirect(url_for('home'))

# Login Logic
@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE email=%s AND password=%s",
        (email, password)
    )
    user = cursor.fetchone()
    cursor.close()

    if user:
        session['user'] = user[1]
        return redirect(url_for('upload_page'))
    else:
        return "Invalid Credentials"

# Upload Page

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_file(os.path.join(UPLOAD_FOLDER, filename))

@app.route('/upload_page')
def upload_page():
    if 'user' in session:
        return render_template("upload.html")
    else:
        return redirect(url_for('home'))

# Upload Logic
@app.route('/upload', methods=['POST'])
def upload():

    if 'file' not in request.files:
        return redirect(url_for('upload_page'))

    file = request.files['file']

    if file.filename == '':
        return redirect(url_for('upload_page'))

    filename = secure_filename(file.filename)

    path = os.path.join(UPLOAD_FOLDER, filename)

    file.save(path)

    # 🔹 Transcribe audio using Whisper
    transcript = transcribe_audio(path)
    summary = summarize_text(transcript)
    print("TRANSCRIPT:", transcript)
    print("SUMMARY:", summary)
    return render_template(
        "upload_success.html",
        filename=filename,
        transcript=transcript,
        summary=summary,
        audio_file=filename 
    )

@app.route('/live_transcribe', methods=['POST'])
def live_transcribe():

    if 'audio' not in request.files:
        return {"error": "No audio received"}

    audio_file = request.files['audio']
    path = os.path.join(UPLOAD_FOLDER, "live.webm")
    audio_file.save(path)

    transcript = transcribe_audio(path)
    summary = summarize_text(transcript)

    return {
        "transcript": transcript,
        "summary": summary
    }

@app.route('/download_txt')
def download_txt():
    transcript = request.args.get('transcript', '')
    summary = request.args.get('summary', '')

    content = f"""Transcript:
{transcript}


Summary:
{summary}
"""

    with open("output.txt", "w", encoding="utf-8") as f:
        f.write(content)

    return send_file("output.txt", as_attachment=True)


@app.route('/download_json')
def download_json():
    transcript = request.args.get('transcript', '')
    summary = request.args.get('summary', '')

    data = {
        "transcript": transcript,
        "summary": summary
    }

    with open("output.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    return send_file("output.json", as_attachment=True)

# Logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return render_template("dashboard.html", name=session['user'])
    else:
        return redirect(url_for('login_page'))


if __name__ == "__main__":
    app.run(debug=True)

