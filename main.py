import os
import tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
import google.generativeai as genai
from pypdf import PdfReader

app = FastAPI()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_API_KEY_HERE")
genai.configure(api_key=GEMINI_API_KEY)

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Soheib AI - منصة الذكاء الاصطناعي</title>
        <style>
            body { font-family: Tahoma, sans-serif; background: #0f172a; color: #f8fafc; padding: 20px; text-align: center; }
            .container { max-width: 600px; margin: auto; background: #1e293b; padding: 30px; border-radius: 15px; box-shadow: 0 10px 25px rgba(0,0,0,0.3); }
            h2 { color: #38bdf8; }
            input, textarea, button { width: 100%; margin-top: 15px; padding: 12px; border-radius: 8px; border: none; font-size: 16px; box-sizing: border-box; }
            textarea { height: 120px; background: #0f172a; color: #fff; }
            button { background: #0284c7; color: #fff; font-weight: bold; cursor: pointer; transition: 0.3s; }
            button:hover { background: #0369a1; }
            .output { background: #0f172a; padding: 15px; border-radius: 8px; margin-top: 20px; text-align: right; min-height: 80px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>مرحباً بك في تطبيق صهيب للذكاء الاصطناعي 🚀</h2>
            <p>ارفع ملف الـ PDF أو اكتب سؤالك:</p>
            <input type="file" id="pdfFile" accept=".pdf">
            <textarea id="promptInput" placeholder="اكتب سؤالك هنا أو اتركها فارغة لقراءة الملزمة وتحليلها..."></textarea>
            <button onclick="sendData()">إرسال وتحليل للذكاء الاصطناعي</button>
            <div class="output" id="outputResult">النتيجة ستظهر هنا...</div>
        </div>
        <script>
            async function sendData() {
                const fileInput = document.getElementById('pdfFile');
                const prompt = document.getElementById('promptInput').value;
                const resultDiv = document.getElementById('outputResult');
                resultDiv.innerText = "جاري المعالجة والتحليل...";
                
                const formData = new FormData();
                if(fileInput.files[0]) formData.append("file", fileInput.files[0]);
                formData.append("prompt", prompt);

                try {
                    const response = await fetch('/analyze', { method: 'POST', body: formData });
                    const data = await response.json();
                    resultDiv.innerText = data.result || data.error;
                } catch(e) {
                    resultDiv.innerText = "حدث خطأ في الاتصال بالسيرفر.";
                }
            }
        </script>
    </body>
    </html>
    """

@app.post("/analyze")
async def analyze(file: UploadFile = File(None), prompt: str = ""):
    extracted_text = ""
    if file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name
        try:
            reader = PdfReader(tmp_path)
            for page in reader.pages:
                text = page.extract_text()
                if text: extracted_text += text + "\n"
        finally:
            os.remove(tmp_path)
            
    full_prompt = f"قم بتحليل النصوص وشرحها بأسلوب تعليمي مبسط:\n{extracted_text}\nالسؤال: {prompt}"
    
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(full_prompt)
        return {"result": response.text}
    except Exception as e:
        return {"error": str(e)}

